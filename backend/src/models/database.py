from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    """Користувачі системи (байєри та адміністратори)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)  # Чи схвалений користувач
    is_admin = Column(Boolean, default=False)     # Чи є адміністратором
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Зв'язки
    tasks = relationship("AutomationTask", back_populates="user")

class FacebookAccount(Base):
    """Facebook аккаунти для автоматизації"""
    __tablename__ = "facebook_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String, nullable=False)  # Назва аккаунта
    geo_location = Column(String, nullable=False)  # BR, US, UK тощо
    encrypted_cookies = Column(Text, nullable=True)  # Зашифровані куки
    encrypted_token = Column(Text, nullable=True)    # Зашифрований токен
    proxy_info = Column(JSON, nullable=True)         # Інформація про проксі
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)      # Чи заблокований аккаунт
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)              # Примітки про аккаунт
    
    # Зв'язки
    tasks = relationship("AutomationTask", back_populates="facebook_account")

class AutomationTask(Base):
    """Завдання автоматизації від байєрів"""
    __tablename__ = "automation_tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    facebook_account_id = Column(Integer, ForeignKey("facebook_accounts.id"), nullable=True)
    
    # Дані завдання
    geo_location = Column(String, nullable=False)    # Вибране гео
    comments = Column(JSON, nullable=False)          # Масив з 8 коментарів
    post_links = Column(JSON, nullable=False)        # Посилання на пости FB
    
    # Статуси завдання
    status = Column(String, default="pending_approval")  # pending_approval, approved, rejected, processing, completed, failed
    admin_notes = Column(Text, nullable=True)            # Примітки адміністратора
    error_message = Column(Text, nullable=True)          # Повідомлення про помилки
    
    # Часові мітки
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Результати виконання
    comments_posted = Column(Integer, default=0)     # Кількість опублікованих коментарів
    execution_log = Column(JSON, nullable=True)      # Лог виконання
    
    # Зв'язки
    user = relationship("User", back_populates="tasks")
    facebook_account = relationship("FacebookAccount", back_populates="tasks")

class TaskExecutionLog(Base):
    """Детальний лог виконання завдань"""
    __tablename__ = "task_execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(36), ForeignKey("automation_tasks.id"), nullable=False)
    step = Column(String, nullable=False)            # Крок виконання
    status = Column(String, nullable=False)          # success, error, warning
    message = Column(Text, nullable=False)           # Повідомлення
    details = Column(JSON, nullable=True)            # Додаткові деталі
    timestamp = Column(DateTime, default=datetime.utcnow)

class SystemSettings(Base):
    """Системні налаштування"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)