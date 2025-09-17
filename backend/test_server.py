from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Создаем приложение FastAPI
app = FastAPI(
    title="CommentFlow API",
    description="API для автоматизации коментарів в соціальних мережах",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "message": "CommentFlow API - Telegram Facebook Bot",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CommentFlow API"}

@app.get("/telegram/check")
async def telegram_check():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        return {"error": "Telegram bot token не настроен"}
    
    # Показываем только первые несколько символов для безопасности
    token_preview = bot_token[:12] + "..." if len(bot_token) > 12 else "настроен"
    return {
        "telegram_configured": True,
        "bot_token_preview": token_preview,
        "message": "Telegram бот успешно настроен!"
    }

if __name__ == "__main__":
    print("🚀 Запуск CommentFlow API...")
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )