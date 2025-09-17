<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>


# Deploy CommentFlow

## Frontend (Vercel)

1. Перейдіть у папку `frontend/` (або корінь, якщо структура однакова).
2. Створіть проект на [Vercel](https://vercel.com/) та підключіть репозиторій.
3. Вкажіть build command: `npm run build` та output directory: `dist`.
4. Додайте змінну оточення `NEXT_PUBLIC_API_URL` з URL вашого backend на Render, наприклад:
   ```
   NEXT_PUBLIC_API_URL=https://commentflow-backend.onrender.com/
   ```
5. Деплойте проект.

## Backend (Render)

1. Перейдіть у папку `backend/`.
2. Створіть новий Web Service на [Render](https://render.com/):
   - Environment: Docker
   - Dockerfile: `backend/Dockerfile`
   - Expose port: 8000
   - Health check path: `/health`
3. Додайте змінні оточення з `.env` (DATABASE_URL, JWT_SECRET_KEY, TELEGRAM_BOT_TOKEN, ENCRYPTION_KEY).
4. Деплойте backend.

## Локальний запуск

### Frontend
```
cd frontend
npm install
npm run dev
```

### Backend
```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Важливо
- Переконайтеся, що у frontend змінна NEXT_PUBLIC_API_URL вказує на Render backend.
- Всі секрети та токени зберігайте у .env або в Render Environment Variables.
