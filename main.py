from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Імпорти локальних модулів
from src.routes import auth, tasks, admin, accounts
from src.services.database import engine, get_db_session
from src.models.database import Base

# Ініціалізація безпеки
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для додатку"""
    # Startup
    print("🚀 Запуск сервера...")
    
    # Створення таблиць бази даних
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ База даних готова")
    
    yield
    
    # Shutdown
    print("🛑 Зупинка сервера...")

# Створення додатку FastAPI
app = FastAPI(
    title="Telegram Facebook Comment Bot API",
    description="API для автоматизації коментарів у Facebook через Telegram Mini App",
    version="1.0.0",
    lifespan=lifespan
)

# CORS налаштування
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend в розробці
        "https://comment-flow-flame.vercel.app"  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Реєстрація маршрутів
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Facebook Accounts"])

@app.get("/")
async def root():
    """Кореневий маршрут"""
    return {
        "message": "Telegram Facebook Comment Bot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check для моніторингу"""
    return {
        "status": "healthy",
        "database": "connected"
    }

@app.get("/api/info")
async def api_info():
    """Інформація про API"""
    return {
        "name": "Telegram Facebook Comment Bot",
        "version": "1.0.0",
        "description": "Система автоматизації коментарів у Facebook",
        "endpoints": {
            "auth": "/api/auth",
            "tasks": "/api/tasks", 
            "admin": "/api/admin",
            "accounts": "/api/accounts"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )