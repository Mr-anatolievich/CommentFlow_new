from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Імпорти локальних модулів
from src.services.database import engine
from src.models.database import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events для додатку"""
    # Startup
    print("🚀 Запуск сервера...")
    
    # Створення таблиць бази даних
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Сервер запущено успішно!")
    
    yield
    
    # Shutdown
    print("🛑 Зупинка сервера...")
    await engine.dispose()
    print("✅ Сервер зупинено!")

# Створення додатку
app = FastAPI(
    title="CommentFlow API",
    description="API для автоматизації коментарів в соціальних мережах",
    version="1.0.0",
    lifespan=lifespan
)

# Налаштування CORS
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

# Базові маршрути
@app.get("/")
async def root():
    return {"message": "CommentFlow API - Telegram Facebook Bot"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CommentFlow API"}

@app.get("/info")
async def api_info():
    return {
        "name": "CommentFlow API",
        "version": "1.0.0",
        "description": "API для автоматизації коментарів",
        "telegram_bot_configured": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
        "database": "SQLite (development)"
    }

# Простая аутентификация для проверки
@app.get("/auth/telegram")
async def telegram_auth_info():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return {"error": "Telegram bot token not configured"}
    
    # Показываем только первые несколько символов токена для безопасности
    masked_token = bot_token[:10] + "..." if len(bot_token) > 10 else "configured"
    return {
        "telegram_bot_configured": True,
        "bot_token_preview": masked_token
    }

if __name__ == "__main__":
    import uvicorn
    
    print("Запуск CommentFlow API сервера...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )