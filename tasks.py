from celery import Celery
from models import Notification
from database import db
import random
from datetime import datetime

celery = Celery("tasks", broker="redis://redis:6379/0")

@celery.task
async def generate_and_send_notification():
    notification = Notification(
        topic=random.choice(["tech", "sports", "news"]),
        release_time=datetime.utcnow(),
        priority=random.choice(["low", "medium", "high"]),
        category=random.choice(["general", "alert", "update"])
    )
    
    # Фильтрация пользователей по предпочтениям
    query = {"subscribed": True}
    for key, value in notification.dict(exclude={"sent_to"}).items():
        query[f"preferences.{key}"] = {"$in": [value]}
    
    users = await db.users.find(query).to_list(length=None)
    user_ids = [str(user["_id"]) for user in users]
    
    # Добавление уведомления в базу
    notification.sent_to = user_ids
    await db.notifications.insert_one(notification.dict())

celery.conf.beat_schedule = {
    "generate-notification-every-minute": {
        "task": "tasks.generate_and_send_notification",
        "schedule": 60.0,
    },
}