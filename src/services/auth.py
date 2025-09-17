from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import hashlib
import hmac
import json
from typing import Optional, Dict, Any
from urllib.parse import unquote

from src.models.database import User
from src.services.database import get_db_session

security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 днів
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Створення JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_telegram_auth(init_data: str) -> Dict[str, Any]:
    """Перевірка автентифікації Telegram Mini App"""
    try:
        # Парсинг init_data
        parsed_data = {}
        for item in init_data.split('&'):
            key, value = item.split('=', 1)
            parsed_data[key] = unquote(value)
        
        # Отримання hash
        received_hash = parsed_data.pop('hash', '')
        
        # Створення рядка для перевірки
        data_check_arr = []
        for key, value in sorted(parsed_data.items()):
            data_check_arr.append(f"{key}={value}")
        data_check_string = '\n'.join(data_check_arr)
        
        # Створення секретного ключа
        secret_key = hmac.new(
            b"WebAppData", 
            TELEGRAM_BOT_TOKEN.encode(), 
            hashlib.sha256
        ).digest()
        
        # Обчислення hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Перевірка hash
        if not hmac.compare_digest(received_hash, calculated_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірні дані автентифікації Telegram"
            )
        
        # Перевірка часу (auth_date не повинен бути старшим за 24 години)
        auth_date = int(parsed_data.get('auth_date', 0))
        current_time = int(datetime.utcnow().timestamp())
        
        if current_time - auth_date > 86400:  # 24 години
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Дані автентифікації застарілі"
            )
        
        # Парсинг даних користувача
        user_data = json.loads(parsed_data.get('user', '{}'))
        
        return user_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Помилка автентифікації: {str(e)}"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """Отримання поточного користувача з JWT токена"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неможливо підтвердити облікові дані",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        telegram_id: str = payload.get("telegram_id")
        if telegram_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Пошук користувача в базі даних
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    # Оновлення останньої активності
    user.last_activity = datetime.utcnow()
    await db.commit()
    
    return user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Перевірка, що поточний користувач є адміністратором"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Потрібні права адміністратора"
        )
    return current_user

async def get_current_approved_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Перевірка, що поточний користувач схвалений"""
    if not current_user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Користувач не схвалений для використання системи"
        )
    return current_user