from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.services.auth import get_current_admin_user
from src.services.database import get_db_session
from src.services.encryption import credential_manager
from src.models.database import FacebookAccount

router = APIRouter()

class FacebookAccountCreate(BaseModel):
    account_name: str
    geo_location: str
    cookies: Dict[str, Any]
    access_token: Optional[str] = None
    proxy_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class FacebookAccountResponse(BaseModel):
    id: int
    account_name: str
    geo_location: str
    is_active: bool
    is_blocked: bool
    has_cookies: bool
    has_token: bool
    has_proxy: bool
    last_used: str | None
    created_at: str
    notes: str | None

class FacebookAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_blocked: Optional[bool] = None
    cookies: Optional[Dict[str, Any]] = None
    access_token: Optional[str] = None
    proxy_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

@router.post("/", response_model=dict)
async def create_facebook_account(
    account_data: FacebookAccountCreate,
    admin_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Створення нового Facebook акаунта"""
    
    # Перевірка унікальності імені акаунта
    existing_result = await db.execute(
        select(FacebookAccount).where(FacebookAccount.account_name == account_data.account_name)
    )
    existing_account = existing_result.scalar_one_or_none()
    
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Акаунт з ім'ям '{account_data.account_name}' вже існує"
        )
    
    # Шифрування чутливих даних
    try:
        encrypted_cookies = credential_manager.encrypt_facebook_cookies(account_data.cookies)
        
        encrypted_token = None
        if account_data.access_token:
            encrypted_token = credential_manager.encrypt_access_token(account_data.access_token)
        
        encrypted_proxy = None
        if account_data.proxy_info:
            encrypted_proxy = credential_manager.encrypt_proxy_info(account_data.proxy_info)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Помилка шифрування даних: {e}"
        )
    
    # Створення акаунта
    new_account = FacebookAccount(
        account_name=account_data.account_name,
        geo_location=account_data.geo_location.upper(),
        encrypted_cookies=encrypted_cookies,
        encrypted_token=encrypted_token,
        proxy_info=encrypted_proxy,
        notes=account_data.notes,
        is_active=True,
        is_blocked=False
    )
    
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    
    print(f"📱 Новий Facebook акаунт створено: {new_account.account_name} ({new_account.geo_location})")
    
    return {
        "account_id": new_account.id,
        "account_name": new_account.account_name,
        "geo_location": new_account.geo_location,
        "message": "Facebook акаунт успішно створено"
    }

@router.get("/", response_model=List[FacebookAccountResponse])
async def get_facebook_accounts(
    geo_location: Optional[str] = None,
    admin_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Отримання списку Facebook акаунтів"""
    
    query = select(FacebookAccount)
    
    if geo_location:
        query = query.where(FacebookAccount.geo_location == geo_location.upper())
    
    query = query.order_by(FacebookAccount.created_at.desc())
    
    result = await db.execute(query)
    accounts = result.scalars().all()
    
    return [
        FacebookAccountResponse(
            id=account.id,
            account_name=account.account_name,
            geo_location=account.geo_location,
            is_active=account.is_active,
            is_blocked=account.is_blocked,
            has_cookies=bool(account.encrypted_cookies),
            has_token=bool(account.encrypted_token),
            has_proxy=bool(account.proxy_info),
            last_used=account.last_used.isoformat() if account.last_used else None,
            created_at=account.created_at.isoformat(),
            notes=account.notes
        )
        for account in accounts
    ]

@router.get("/{account_id}", response_model=FacebookAccountResponse)
async def get_facebook_account(
    account_id: int,
    admin_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Отримання конкретного Facebook акаунта"""
    
    result = await db.execute(
        select(FacebookAccount).where(FacebookAccount.id == account_id)
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facebook акаунт не знайдено"
        )
    
    return FacebookAccountResponse(
        id=account.id,
        account_name=account.account_name,
        geo_location=account.geo_location,
        is_active=account.is_active,
        is_blocked=account.is_blocked,
        has_cookies=bool(account.encrypted_cookies),
        has_token=bool(account.encrypted_token),
        has_proxy=bool(account.proxy_info),
        last_used=account.last_used.isoformat() if account.last_used else None,
        created_at=account.created_at.isoformat(),
        notes=account.notes
    )

@router.put("/{account_id}", response_model=dict)
async def update_facebook_account(
    account_id: int,
    update_data: FacebookAccountUpdate,
    admin_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Оновлення Facebook акаунта"""
    
    result = await db.execute(
        select(FacebookAccount).where(FacebookAccount.id == account_id)
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facebook акаунт не знайдено"
        )
    
    # Оновлення базових полів
    if update_data.account_name is not None:
        account.account_name = update_data.account_name
    
    if update_data.is_active is not None:
        account.is_active = update_data.is_active
    
    if update_data.is_blocked is not None:
        account.is_blocked = update_data.is_blocked
    
    if update_data.notes is not None:
        account.notes = update_data.notes
    
    # Оновлення зашифрованих даних
    try:
        if update_data.cookies is not None:
            account.encrypted_cookies = credential_manager.encrypt_facebook_cookies(update_data.cookies)
        
        if update_data.access_token is not None:
            if update_data.access_token:
                account.encrypted_token = credential_manager.encrypt_access_token(update_data.access_token)
            else:
                account.encrypted_token = None
        
        if update_data.proxy_info is not None:
            if update_data.proxy_info:
                account.proxy_info = credential_manager.encrypt_proxy_info(update_data.proxy_info)
            else:
                account.proxy_info = None
                
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Помилка шифрування даних: {e}"
        )
    
    await db.commit()
    
    print(f"🔄 Facebook акаунт оновлено: {account.account_name}")
    
    return {
        "account_id": account.id,
        "message": "Facebook акаунт успішно оновлено"
    }

@router.delete("/{account_id}")
async def delete_facebook_account(
    account_id: int,
    admin_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Видалення Facebook акаунта"""
    
    result = await db.execute(
        select(FacebookAccount).where(FacebookAccount.id == account_id)
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facebook акаунт не знайдено"
        )
    
    account_name = account.account_name
    await db.delete(account)
    await db.commit()
    
    print(f"🗑️ Facebook акаунт видалено: {account_name}")
    
    return {"message": f"Facebook акаунт '{account_name}' видалено"}

@router.get("/{account_id}/test-connection")
async def test_facebook_account_connection(
    account_id: int,
    admin_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Тестування з'єднання з Facebook акаунтом"""
    
    result = await db.execute(
        select(FacebookAccount).where(FacebookAccount.id == account_id)
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Facebook акаунт не знайдено"
        )
    
    if not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Акаунт неактивний"
        )
    
    # TODO: Реалізувати тестування з'єднання через браузерну автоматизацію
    # Поки що просто перевіримо наявність даних
    
    has_cookies = bool(account.encrypted_cookies)
    has_token = bool(account.encrypted_token)
    
    if not has_cookies:
        return {
            "status": "error",
            "message": "Відсутні куки для автентифікації"
        }
    
    return {
        "status": "success",
        "message": "Базові дані для з'єднання присутні",
        "details": {
            "has_cookies": has_cookies,
            "has_token": has_token,
            "has_proxy": bool(account.proxy_info),
            "last_used": account.last_used.isoformat() if account.last_used else "Ніколи"
        }
    }