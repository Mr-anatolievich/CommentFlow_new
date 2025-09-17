from celery import Celery
import os
from typing import Optional

# Налаштування Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Створення екземпляра Celery
celery_app = Celery(
    "automation_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.tasks.automation"]
)

# Конфігурація Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 хвилин
    task_soft_time_limit=25 * 60,  # 25 хвилин
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_always_eager=False,  # Встановити True для тестування без Redis
)

# Маршрутизація завдань
celery_app.conf.task_routes = {
    "src.tasks.automation.process_facebook_comments": {"queue": "facebook_automation"},
    "src.tasks.automation.setup_facebook_session": {"queue": "facebook_setup"},
    "src.tasks.automation.cleanup_facebook_session": {"queue": "facebook_cleanup"},
}

# Налаштування черг
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_create_missing_queues = True

async def queue_automation_task(task_id: str, priority: int = 5) -> str:
    """Додавання завдання автоматизації до черги"""
    try:
        result = celery_app.send_task(
            "src.tasks.automation.process_facebook_comments",
            args=[task_id],
            queue="facebook_automation",
            priority=priority,
            retry=True,
            retry_policy={
                'max_retries': 3,
                'interval_start': 0,
                'interval_step': 60,
                'interval_max': 600,
            }
        )
        
        print(f"✅ Завдання {task_id} додано до черги: {result.id}")
        return result.id
        
    except Exception as e:
        print(f"❌ Помилка додавання завдання до черги: {e}")
        raise

def get_task_status(celery_task_id: str) -> dict:
    """Отримання статусу завдання Celery"""
    try:
        result = celery_app.AsyncResult(celery_task_id)
        return {
            "task_id": celery_task_id,
            "status": result.status,
            "result": result.result,
            "traceback": result.traceback
        }
    except Exception as e:
        return {
            "task_id": celery_task_id,
            "status": "ERROR",
            "result": str(e),
            "traceback": None
        }

def cancel_task(celery_task_id: str) -> bool:
    """Скасування завдання Celery"""
    try:
        celery_app.control.revoke(celery_task_id, terminate=True)
        print(f"🚫 Завдання {celery_task_id} скасовано")
        return True
    except Exception as e:
        print(f"❌ Помилка скасування завдання: {e}")
        return False

# Періодичні завдання (Celery Beat)
celery_app.conf.beat_schedule = {
    # Очищення застарілих завдань кожні 6 годин
    'cleanup-old-tasks': {
        'task': 'src.tasks.maintenance.cleanup_old_tasks',
        'schedule': 6 * 60 * 60,  # 6 годин
    },
    # Перевірка стану Facebook акаунтів щодня
    'check-facebook-accounts': {
        'task': 'src.tasks.maintenance.check_facebook_accounts_health',
        'schedule': 24 * 60 * 60,  # 24 години
    },
}

# Налаштування для розробки
if os.getenv("DEVELOPMENT") == "true":
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True