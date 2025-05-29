import os
import random
from celery import Celery
from datetime import datetime
import aiosmtplib
from email.mime.text import MIMEText
from motor.motor_asyncio import AsyncIOMotorClient

# Инициализация Celery
app = Celery('tasks', broker=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0'))

# Настройка MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017')
client = AsyncIOMotorClient(MONGO_URI)
db = client['sigmora']
users_collection = db['users']
notifications_collection = db['notifications']

# SMTP настройки из переменных окружения
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
SMTP_FROM = os.getenv('SMTP_FROM', 'no-reply@sigmora.com')

async def send_email(to_email: str, subject: str, body: str):
    """Асинхронная отправка email с помощью aiosmtplib."""
    message = MIMEText(body)
    message['From'] = SMTP_FROM
    message['To'] = to_email
    message['Subject'] = subject

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            use_tls=True,
        )
        print(f"Email успешно отправлен на {to_email}")
    except Exception as e:
        print(f"Ошибка при отправке email на {to_email}: {str(e)}")

@app.task
async def generate_and_send_notification():
    """Генерация и отправка уведомлений пользователям с соответствующими предпочтениями."""
    # Список возможных параметров уведомления
    topics = ['tech', 'sports', 'news']
    priorities = ['low', 'medium', 'high']
    categories = ['general', 'alert', 'update']

    # Генерация случайного уведомления
    notification = {
        'topic': random.choice(topics),
        'priority': random.choice(priorities),
        'category': random.choice(categories),
        'release_time': datetime.utcnow(),
        'content': f"Новое уведомление: {random.choice(topics)} (приоритет: {random.choice(priorities)})",
        'recipients': []
    }

    # Поиск пользователей с соответствующими предпочтениями
    query = {
        'subscribed': True,
        'preferences.topics': notification['topic'],
        'preferences.priority': notification['priority'],
        'preferences.category': notification['category']
    }
    users = users_collection.find(query)

    async for user in users:
        email = user['email']
        notification['recipients'].append(email)

        # Отправка email
        subject = f"Sigmora: {notification['topic'].capitalize()} Notification"
        body = f"""
        Здравствуйте,

        Вы получили новое уведомление:
        Тема: {notification['topic']}
        Приоритет: {notification['priority']}
        Категория: {notification['category']}
        Сообщение: {notification['content']}
        Время: {notification['release_time']}

        Отписаться: http://localhost:8000/unsubscribe
        """
        await send_email(email, subject, body)

    # Сохранение уведомления в MongoDB
    await notifications_collection.insert_one(notification)
    print(f"Уведомление отправлено {len(notification['recipients'])} пользователям")