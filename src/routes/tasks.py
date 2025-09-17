from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime

from src.services.auth import get_current_approved_user, get_current_user
from src.services.database import get_db_session
from src.models.database import User, AutomationTask, FacebookAccount
from src.services.queue import queue_automation_task

router = APIRouter()

class TaskCreateRequest(BaseModel):
    geo_location: str = Field(..., min_length=2, max_length=5, description="Код країни (BR, US, UK тощо)")
    comments: List[str] = Field(..., min_items=8, max_items=8, description="Рівно 8 коментарів")
    post_links: List[str] = Field(..., min_items=1, max_items=10, description="Посилання на Facebook пости")

class TaskResponse(BaseModel):
    id: str
    geo_location: str
    comments: List[str]
    post_links: List[str]
    status: str
    comments_posted: int
    created_at: str
    started_at: str | None
    completed_at: str | None
    admin_notes: str | None
    error_message: str | None

class TaskStatusUpdate(BaseModel):
    status: str
    admin_notes: str | None = None

# Підтримувані гео локації
SUPPORTED_GEOS = ["BR", "US", "UK", "DE", "FR", "ES", "IT", "CA", "AU", "MX"]

@router.post("/", response_model=dict)
async def create_task(
    task_data: TaskCreateRequest,
    current_user: User = Depends(get_current_approved_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Створення нового завдання автоматизації"""
    
    # Перевірка підтримуваних гео
    if task_data.geo_location not in SUPPORTED_GEOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Непідтримувана гео локація. Доступні: {', '.join(SUPPORTED_GEOS)}"
        )
    
    # Перевірка кількості коментарів
    if len(task_data.comments) != 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Потрібно рівно 8 коментарів"
        )
    
    # Перевірка наявності доступних акаунтів для гео
    result = await db.execute(
        select(FacebookAccount).where(
            and_(
                FacebookAccount.geo_location == task_data.geo_location,
                FacebookAccount.is_active == True,
                FacebookAccount.is_blocked == False
            )
        )
    )
    available_accounts = result.scalars().all()
    
    if not available_accounts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Немає доступних Facebook акаунтів для гео {task_data.geo_location}"
        )
    
    # Створення завдання
    new_task = AutomationTask(
        user_id=current_user.id,
        geo_location=task_data.geo_location,
        comments=task_data.comments,
        post_links=task_data.post_links,
        status="pending_approval"
    )
    
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    
    print(f"📋 Нове завдання створено: {new_task.id} для користувача {current_user.username}")
    
    return {
        "task_id": str(new_task.id),
        "status": "submitted_for_approval",
        "message": "Завдання подано на розгляд адміністратора"
    }

@router.get("/", response_model=List[TaskResponse])
async def get_user_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Отримання завдань поточного користувача"""
    
    result = await db.execute(
        select(AutomationTask)
        .where(AutomationTask.user_id == current_user.id)
        .order_by(AutomationTask.created_at.desc())
    )
    tasks = result.scalars().all()
    
    return [
        TaskResponse(
            id=str(task.id),
            geo_location=task.geo_location,
            comments=task.comments,
            post_links=task.post_links,
            status=task.status,
            comments_posted=task.comments_posted,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            admin_notes=task.admin_notes,
            error_message=task.error_message
        )
        for task in tasks
    ]

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Отримання конкретного завдання"""
    
    # Використовуємо task_id як рядок, оскільки тепер UUID зберігається як String(36)
    if not task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невірний формат ID завдання"
        )
    
    result = await db.execute(
        select(AutomationTask).where(
            and_(
                AutomationTask.id == task_id,
                AutomationTask.user_id == current_user.id
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Завдання не знайдено"
        )
    
    return TaskResponse(
        id=str(task.id),
        geo_location=task.geo_location,
        comments=task.comments,
        post_links=task.post_links,
        status=task.status,
        comments_posted=task.comments_posted,
        created_at=task.created_at.isoformat(),
        started_at=task.started_at.isoformat() if task.started_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
        admin_notes=task.admin_notes,
        error_message=task.error_message
    )

@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Скасування завдання (тільки якщо воно ще не виконується)"""
    
    # Використовуємо task_id як рядок, оскільки тепер UUID зберігається як String(36)
    if not task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невірний формат ID завдання"
        )
    
    result = await db.execute(
        select(AutomationTask).where(
            and_(
                AutomationTask.id == task_id,
                AutomationTask.user_id == current_user.id
            )
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Завдання не знайдено"
        )
    
    if task.status not in ["pending_approval", "approved"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неможливо скасувати завдання, що вже виконується або завершено"
        )
    
    await db.delete(task)
    await db.commit()
    
    return {"message": "Завдання скасовано"}

@router.get("/supported/geos")
async def get_supported_geos():
    """Отримання списку підтримуваних гео локацій"""
    return {
        "supported_geos": SUPPORTED_GEOS,
        "descriptions": {
            "BR": "Бразилія",
            "US": "США", 
            "UK": "Великобританія",
            "DE": "Німеччина",
            "FR": "Франція",
            "ES": "Іспанія",
            "IT": "Італія",
            "CA": "Канада",
            "AU": "Австралія",
            "MX": "Мексика"
        }
    }