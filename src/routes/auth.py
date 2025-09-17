from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from src.services.auth import verify_telegram_auth, create_access_token, get_current_user
from src.services.database import get_db_session
from src.models.database import User

router = APIRouter()

class TelegramAuthRequest(BaseModel):
    initData: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserInfo(BaseModel):
    id: int
    telegram_id: str
    username: str | None
    first_name: str | None
    is_approved: bool
    is_admin: bool

@router.post("/login", response_model=AuthResponse)
async def login(
    auth_request: TelegramAuthRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Авторизація користувача через Telegram Mini App"""
    
    # Перевірка даних Telegram
    telegram_user = verify_telegram_auth(auth_request.initData)
    
    telegram_id = str(telegram_user.get("id"))
    username = telegram_user.get("username")
    first_name = telegram_user.get("first_name")
    last_name = telegram_user.get("last_name")
    
    # Пошук існуючого користувача
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    # Створення нового користувача якщо не існує
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_approved=False,  # Потрібне схвалення адміністратора
            is_admin=False
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        print(f"📝 Новий користувач зареєстрований: {username} (ID: {telegram_id})")
    else:
        # Оновлення даних існуючого користувача
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.last_activity = datetime.utcnow()
        await db.commit()
    
    # Створення JWT токена
    access_token = create_access_token(
        data={"telegram_id": user.telegram_id}
    )
    
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "is_approved": user.is_approved,
            "is_admin": user.is_admin
        }
    )

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Отримання інформації про поточного користувача"""
    return UserInfo(
        id=current_user.id,
        telegram_id=current_user.telegram_id,
        username=current_user.username,
        first_name=current_user.first_name,
        is_approved=current_user.is_approved,
        is_admin=current_user.is_admin
    )

@router.post("/check-approval")
async def check_user_approval(
    current_user: User = Depends(get_current_user)
):
    """Перевірка статусу схвалення користувача"""
    return {
        "is_approved": current_user.is_approved,
        "is_admin": current_user.is_admin,
        "message": "Схвалено" if current_user.is_approved else "Очікує схвалення адміністратора"
    }