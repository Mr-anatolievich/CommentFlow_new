from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select, update
import asyncio
import logging
import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional
import sys

# Додаємо шлях до backend для імпорту
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from src.models.database import AutomationTask, FacebookAccount, TaskExecutionLog
from src.services.encryption import credential_manager
from src.services.queue import celery_app
from automation.src.browser_manager import BrowserManager
from automation.src.facebook_automation import FacebookCommentBot

logger = logging.getLogger(__name__)

# Налаштування бази даних для завдань
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://automation_user:defaultpassword@localhost/automation_db")
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    """Отримання сесії бази даних"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@celery_app.task(bind=True, max_retries=3)
def process_facebook_comments(self, task_id: str):
    """Основне завдання Celery для обробки коментарів Facebook"""
    
    logger.info(f"🚀 Початок обробки завдання {task_id}")
    
    try:
        # Запуск асинхронної обробки
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_process_comments_async(self, task_id))
        loop.close()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Критична помилка завдання {task_id}: {e}")
        
        # Оновлення статусу завдання в БД
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_update_task_status(task_id, "failed", str(e)))
        loop.close()
        
        # Повторна спроба якщо не вичерпано ліміт
        if self.request.retries < self.max_retries:
            logger.info(f"🔄 Повторна спроба {self.request.retries + 1}/{self.max_retries}")
            raise self.retry(countdown=60 * (self.request.retries + 1))  # Експоненційна затримка
        
        raise

async def _process_comments_async(celery_task, task_id: str) -> Dict:
    """Асинхронна обробка коментарів"""
    
    browser_manager = None
    task = None
    facebook_account = None
    
    try:
        # Отримання завдання з БД
        async for db in get_db_session():
            result = await db.execute(
                select(AutomationTask).where(AutomationTask.id == task_id)
            )
            task = result.scalar_one_or_none()
            break
        
        if not task:
            raise Exception(f"Завдання {task_id} не знайдено в БД")
        
        if task.status != "approved":
            raise Exception(f"Завдання {task_id} не схвалено для виконання")
        
        # Оновлення статусу на "processing"
        await _update_task_status(task_id, "processing")
        
        # Отримання Facebook аккаунта
        async for db in get_db_session():
            result = await db.execute(
                select(FacebookAccount).where(
                    FacebookAccount.geo_location == task.geo_location and
                    FacebookAccount.is_active == True and
                    FacebookAccount.is_blocked == False
                )
            )
            facebook_account = result.scalars().first()
            break
        
        if not facebook_account:
            raise Exception(f"Немає доступних Facebook аккаунтів для {task.geo_location}")
        
        # Розшифровка даних аккаунта
        cookies = credential_manager.decrypt_facebook_cookies(facebook_account.encrypted_cookies)
        
        proxy_info = None
        if facebook_account.proxy_info:
            proxy_info = credential_manager.decrypt_proxy_info(facebook_account.proxy_info)
        
        # Ініціалізація браузера
        browser_manager = BrowserManager()
        browser = await browser_manager.init_browser(headless=True)
        context = await browser_manager.create_context(
            cookies=cookies,
            proxy=proxy_info,
            geo_location=task.geo_location
        )
        page = await context.new_page()
        
        # Ініціалізація бота для коментарів
        comment_bot = FacebookCommentBot(page)
        
        # Лог початку виконання
        await _log_task_execution(task_id, "start", "success", f"Розпочато обробку з аккаунтом {facebook_account.account_name}")
        
        comments_posted = 0
        total_comments = len(task.comments) * len(task.post_links)
        
        # Обробка кожного поста
        for post_index, post_url in enumerate(task.post_links):
            logger.info(f"📝 Обробка поста {post_index + 1}/{len(task.post_links)}: {post_url}")
            
            # Навігація до поста
            if not await comment_bot.navigate_to_post(post_url):
                await _log_task_execution(
                    task_id, "navigation", "error", 
                    f"Не вдалося завантажити пост: {post_url}"
                )
                continue
            
            await _log_task_execution(
                task_id, "navigation", "success", 
                f"Успішно завантажено пост: {post_url}"
            )
            
            # Публікація кожного коментаря
            for comment_index, comment in enumerate(task.comments):
                logger.info(f"💬 Публікація коментаря {comment_index + 1}/{len(task.comments)}")
                
                # Перевірка блокувань
                if not await comment_bot.handle_potential_blocks():
                    await _log_task_execution(
                        task_id, "block_check", "error",
                        "Виявлено блокування аккаунта"
                    )
                    
                    # Позначаємо аккаунт як заблокований
                    async for db in get_db_session():
                        await db.execute(
                            update(FacebookAccount)
                            .where(FacebookAccount.id == facebook_account.id)
                            .values(is_blocked=True)
                        )
                        await db.commit()
                        break
                    break
                
                # Публікація коментаря
                success = await comment_bot.post_comment(comment)
                
                if success:
                    comments_posted += 1
                    await _log_task_execution(
                        task_id, "comment", "success",
                        f"Коментар опубліковано: {comment[:50]}..."
                    )
                    logger.info(f"✅ Коментар {comment_index + 1} опубліковано")
                else:
                    await _log_task_execution(
                        task_id, "comment", "error",
                        f"Не вдалося опублікувати: {comment[:50]}..."
                    )
                    logger.error(f"❌ Помилка публікації коментаря {comment_index + 1}")
                
                # Оновлення прогресу
                progress = (comments_posted / total_comments) * 100
                celery_task.update_state(
                    state='PROGRESS',
                    meta={
                        'current': comments_posted,
                        'total': total_comments,
                        'progress': progress,
                        'status': f'Опубліковано {comments_posted}/{total_comments} коментарів'
                    }
                )
                
                # Випадкова затримка між коментарями (30-120 секунд)
                delay = random.randint(30, 120)
                logger.info(f"⏰ Затримка {delay} секунд між коментарями")
                await asyncio.sleep(delay)
            
            # Затримка між постами (5-10 хвилин)
            if post_index < len(task.post_links) - 1:  # Не затримуємося після останнього поста
                delay = random.randint(300, 600)
                logger.info(f"⏰ Затримка {delay} секунд між постами")
                await asyncio.sleep(delay)
        
        # Оновлення аккаунта
        async for db in get_db_session():
            await db.execute(
                update(FacebookAccount)
                .where(FacebookAccount.id == facebook_account.id)
                .values(last_used=datetime.utcnow())
            )
            await db.commit()
            break
        
        # Завершення завдання
        await _update_task_status(
            task_id, "completed", 
            comments_posted=comments_posted,
            facebook_account_id=facebook_account.id
        )
        
        await _log_task_execution(
            task_id, "completion", "success",
            f"Завдання завершено. Опубліковано {comments_posted}/{total_comments} коментарів"
        )
        
        logger.info(f"🎉 Завдання {task_id} успішно завершено")
        
        return {
            "status": "completed",
            "comments_posted": comments_posted,
            "total_comments": total_comments,
            "facebook_account": facebook_account.account_name
        }
        
    except Exception as e:
        logger.error(f"❌ Помилка обробки завдання {task_id}: {e}")
        
        if task:
            await _update_task_status(task_id, "failed", str(e))
        
        await _log_task_execution(
            task_id, "error", "error", str(e)
        )
        
        raise
    
    finally:
        if browser_manager:
            await browser_manager.close()

async def _update_task_status(
    task_id: str, 
    status: str, 
    error_message: Optional[str] = None,
    comments_posted: Optional[int] = None,
    facebook_account_id: Optional[int] = None
):
    """Оновлення статусу завдання в БД"""
    try:
        async for db in get_db_session():
            update_data = {"status": status}
            
            if status == "processing":
                update_data["started_at"] = datetime.utcnow()
            elif status in ["completed", "failed"]:
                update_data["completed_at"] = datetime.utcnow()
            
            if error_message:
                update_data["error_message"] = error_message
            
            if comments_posted is not None:
                update_data["comments_posted"] = comments_posted
            
            if facebook_account_id:
                update_data["facebook_account_id"] = facebook_account_id
            
            await db.execute(
                update(AutomationTask)
                .where(AutomationTask.id == task_id)
                .values(**update_data)
            )
            await db.commit()
            break
            
    except Exception as e:
        logger.error(f"Помилка оновлення статусу завдання: {e}")

async def _log_task_execution(
    task_id: str,
    step: str,
    status: str,
    message: str,
    details: Optional[Dict] = None
):
    """Логування виконання завдання"""
    try:
        async for db in get_db_session():
            log_entry = TaskExecutionLog(
                task_id=task_id,
                step=step,
                status=status,
                message=message,
                details=details or {},
                timestamp=datetime.utcnow()
            )
            db.add(log_entry)
            await db.commit()
            break
            
    except Exception as e:
        logger.error(f"Помилка логування: {e}")