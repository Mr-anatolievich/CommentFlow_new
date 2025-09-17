from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, func
from typing import List, Optional
from datetime import datetime

from src.services.auth import get_current_admin_user
from src.services.database import get_db_session
from src.models.database import User, AutomationTask, FacebookAccount
from src.services.queue import queue_automation_task

router = APIRouter()

class PendingTaskResponse(BaseModel):
    id: str
    user_id: int
    username: str | None
    first_name: str | None
    geo_location: str
    comments: List[str]
    post_links: List[str]
    created_at: str

class UserApprovalRequest(BaseModel):
    user_id: int
    is_approved: bool
    is_admin: bool = False

class TaskApprovalRequest(BaseModel):
    task_id: str
    action: str  # "approve" або "reject"
    admin_notes: Optional[str] = None

class UserListResponse(BaseModel):
    id: int
    telegram_id: str
    username: str | None
    first_name: str | None
    is_approved: bool
    is_admin: bool
    created_at: str
    last_activity: str
    tasks_count: int

@router.get("/pending-tasks", response_model=List[PendingTaskResponse])
async def get_pending_tasks(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Отримання завдань, що очікують схвалення"""
    
    result = await db.execute(
        select(AutomationTask, User)
        .join(User, AutomationTask.user_id == User.id)
        .where(AutomationTask.status == "pending_approval")
        .order_by(AutomationTask.created_at.asc())
    )
    
    tasks_and_users = result.all()
    
    return [
        PendingTaskResponse(
            id=str(task.id),
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            geo_location=task.geo_location,
            comments=task.comments,
            post_links=task.post_links,
            created_at=task.created_at.isoformat()
        )
        for task, user in tasks_and_users
    ]

@router.post("/approve-task")
async def approve_or_reject_task(
    approval_request: TaskApprovalRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Схвалення або відхилення завдання"""
    
    # Використовуємо task_id як рядок, оскільки тепер UUID зберігається як String(36)
    if not approval_request.task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невірний формат ID завдання"
        )
    
    # Пошук завдання
    result = await db.execute(
        select(AutomationTask).where(AutomationTask.id == approval_request.task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Завдання не знайдено"
        )
    
    if task.status != "pending_approval":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Завдання вже оброблено"
        )
    
    if approval_request.action == "approve":
        # Схвалення завдання
        task.status = "approved"
        task.approved_at = datetime.utcnow()
        task.admin_notes = approval_request.admin_notes
        
        await db.commit()
        
        # Додавання до черги виконання
        try:
            await queue_automation_task(str(task.id))
            message = f"Завдання {task.id} схвалено та додано до черги виконання"
        except Exception as e:
            message = f"Завдання схвалено, але помилка додавання до черги: {e}"
        
        print(f"✅ Адмін {admin_user.username} схвалив завдання {task.id}")
        
    elif approval_request.action == "reject":
        # Відхилення завдання
        task.status = "rejected"
        task.admin_notes = approval_request.admin_notes or "Відхилено адміністратором"
        
        await db.commit()
        
        message = f"Завдання {task.id} відхилено"
        print(f"❌ Адмін {admin_user.username} відхилив завдання {task.id}")
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невірна дія. Використовуйте 'approve' або 'reject'"
        )
    
    return {"message": message, "task_id": str(task.id), "status": task.status}

@router.get("/users", response_model=List[UserListResponse])
async def get_all_users(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Отримання списку всіх користувачів"""
    
    # Отримання користувачів з кількістю завдань
    result = await db.execute(
        select(User, func.count(AutomationTask.id).label('tasks_count'))
        .outerjoin(AutomationTask, User.id == AutomationTask.user_id)
        .group_by(User.id)
        .order_by(User.created_at.desc())
    )
    
    users_with_counts = result.all()
    
    return [
        UserListResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            is_approved=user.is_approved,
            is_admin=user.is_admin,
            created_at=user.created_at.isoformat(),
            last_activity=user.last_activity.isoformat() if user.last_activity else user.created_at.isoformat(),
            tasks_count=tasks_count
        )
        for user, tasks_count in users_with_counts
    ]

@router.post("/approve-user")
async def approve_user(
    approval_request: UserApprovalRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Схвалення або блокування користувача"""
    
    # Пошук користувача
    result = await db.execute(
        select(User).where(User.id == approval_request.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Користувача не знайдено"
        )
    
    # Оновлення статусу користувача
    user.is_approved = approval_request.is_approved
    
    # Встановлення прав адміністратора (тільки якщо користувач схвалений)
    if approval_request.is_approved and approval_request.is_admin:
        user.is_admin = True
    else:
        user.is_admin = False
    
    await db.commit()
    
    action = "схвалено" if approval_request.is_approved else "заблоковано"
    admin_suffix = " як адміністратор" if user.is_admin else ""
    
    print(f"👤 Адмін {admin_user.username} {action} користувача {user.username}{admin_suffix}")
    
    return {
        "message": f"Користувача {user.username} {action}{admin_suffix}",
        "user_id": user.id,
        "is_approved": user.is_approved,
        "is_admin": user.is_admin
    }

@router.get("/stats")
async def get_admin_stats(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Отримання статистики для адміністративної панелі"""
    
    # Загальна кількість користувачів
    total_users_result = await db.execute(select(func.count(User.id)))
    total_users = total_users_result.scalar()
    
    # Схвалені користувачі
    approved_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_approved == True)
    )
    approved_users = approved_users_result.scalar()
    
    # Завдання за статусами
    tasks_stats_result = await db.execute(
        select(AutomationTask.status, func.count(AutomationTask.id))
        .group_by(AutomationTask.status)
    )
    tasks_stats = dict(tasks_stats_result.all())
    
    # Доступні Facebook акаунти за гео
    accounts_stats_result = await db.execute(
        select(FacebookAccount.geo_location, func.count(FacebookAccount.id))
        .where(and_(FacebookAccount.is_active == True, FacebookAccount.is_blocked == False))
        .group_by(FacebookAccount.geo_location)
    )
    accounts_stats = dict(accounts_stats_result.all())
    
    return {
        "users": {
            "total": total_users,
            "approved": approved_users,
            "pending": total_users - approved_users
        },
        "tasks": tasks_stats,
        "facebook_accounts": accounts_stats,
        "updated_at": datetime.utcnow().isoformat()
    }