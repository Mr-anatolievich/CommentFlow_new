from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from typing import AsyncGenerator

# Отримання URL бази даних з змінних середовища
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./automation.db")

# Створення асинхронного двигуна
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # Логування SQL запитів (вимкнути в продакшені)
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL configuration
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # Логування SQL запитів (вимкнути в продакшені)
        pool_size=20,
        max_overflow=0,
        pool_pre_ping=True,
        pool_recycle=300,
    )

# Створення фабрики сесій
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Базовий клас для моделей
Base = declarative_base()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор сесій бази даних для FastAPI Dependency Injection"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_database():
    """Ініціалізація бази даних"""
    from src.models.database import Base
    
    async with engine.begin() as conn:
        # Створити всі таблиці
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблиці бази даних створено")

async def close_database():
    """Закриття з'єднання з базою даних"""
    await engine.dispose()
    print("🔌 З'єднання з базою даних закрито")