# Гайд по установке и использованию Sigmora Notification Service

**Sigmora Notification Service** — это сервис уведомлений на базе FastAPI, MongoDB и Celery, который позволяет подписываться на уведомления, настраивать предпочтения (темы, приоритеты, категории) и получать их по email. Сервис использует Python 3.13, контейнеризирован через Docker Compose и отправляет email с помощью библиотеки aiosmtplib. Этот гайд поможет вам запустить сервис, настроить отправку email и протестировать его.

**Репозиторий**: https://github.com/GendByteMaster/

## Что вам понадобится

- **Docker** и **Docker Compose** (для контейнеризированного запуска).
- **Python 3.13** (если запускаете без Docker).
- **SMTP-учетные данные** (например, Gmail с App Password или другой SMTP-сервер).
- Доступ к папке проекта (на Windows: настройте общий доступ в Docker Desktop для G:\\Repository\\Sigmora).

## Шаг 1: Клонирование и настройка

1. **Клонируйте репозиторий**:

   ```bash
   git clone https://github.com/GendByteMaster/sigmora.git
   cd sigmora
   ```

2. **Создайте файл** .env: Скопируйте пример конфигурации:

   ```bash
   cp .env.example .env
   ```

   Отредактируйте .env, добавив:

   ```env
   SECRET_KEY=your-secure-secret-key
   MONGO_URI=mongodb://mongo:27017
   CELERY_BROKER_URL=redis://redis:6379/0
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_FROM=no-reply@sigmora.com
   ```

   **Примечание**: Для Gmail создайте App Password в Google Account &gt; Безопасность &gt; Пароли приложений.

3. **Проверьте доступ (Windows)**: В Docker Desktop &gt; Настройки &gt; Ресурсы &gt; Общий доступ добавьте G:\\Repository\\Sigmora.

## Шаг 2: Запуск сервиса

1. **Соберите и запустите**:

   ```bash
   docker-compose up --build
   ```

   Если ошибки, пересоберите:

   ```bash
   docker-compose build --no-cache
   docker-compose up
   ```

2. **Проверьте сервисы**:

   - API: `http://localhost:8000`
   - Документация: `http://localhost:8000/docs`
   - Логи: `docker-compose logs api` или `docker-compose logs celery`

3. **Остановка**:

   ```bash
   docker-compose down
   ```

## Шаг 3: Тестирование API

1. **Создайте пользователя**:

   ```bash
   curl -X POST "http://localhost:8000/subscribe" -H "Content-Type: application/json" -d '{
     "email": "the.hendrik@yandex.ru",
     "password": "securepassword",
     "subscribed": true,
     "preferences": {"topics": ["tech"], "priority": ["high"], "category": ["alert"]}
   }'
   ```

2. **Получите JWT-токен**:

   ```bash
   curl -X POST "http://localhost:8000/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=the.hendrik@yandex.ru&password=securepassword"
   ```

3. **Обновите предпочтения** (опционально):

   ```bash
   curl -X POST "http://localhost:8000/preferences" -H "Authorization: Bearer <JWT_TOKEN>" -H "Content-Type: application/json" -d '{
     "topics": ["tech", "news"],
     "priority": ["high", "medium"],
     "category": ["alert", "update"]
   }'
   ```

4. **Проверьте уведомления**:

   ```bash
   curl -X GET "http://localhost:8000/notifications" -H "Authorization: Bearer <JWT_TOKEN>"
   ```

## Шаг 4: Проверка отправки email

1. **Дождитесь уведомления**: Celery отправляет уведомления каждые 60 секунд. Проверьте логи:

   ```bash
   docker-compose logs celery
   ```

2. **Проверьте почту**: Ищите письмо с темой `Sigmora: Tech Notification` в `the.hendrik@yandex.ru` (проверьте "Спам").

3. **Тест SMTP** (если email не приходит):

   ```bash
   docker exec -it sigmora-celery-1 python -c "import asyncio, aiosmtplib; from email.mime.text import MIMEText; async def test(): await aiosmtplib.send(MIMEText('Test'), hostname='smtp.gmail.com', port=587, username='your-email@gmail.com', password='your-app-password', use_tls=True, sender='no-reply@sigmora.com', recipients=['the.hendrik@yandex.ru']); asyncio.run(test())"
   ```

## Шаг 5: Устранение неполадок

- **API не работает**: Проверьте логи (`docker-compose logs api`), убедитесь, что `python-multipart==0.0.12` установлен.
- **Email не отправляется**: Проверьте `.env`, используйте App Password для Gmail, проверьте логи Celery.
- **Ошибка** `/token`: Убедитесь, что пользователь создан, проверьте email/пароль в MongoDB (`docker exec -it sigmora-mongo-1 mongosh`).
- **Python 3.13**: Обновите зависимости (например, `motor==3.7.0`) в `pyproject.toml` при ошибках.
- **Windows**: Настройте доступ к `G:\Repository\Sigmora` в Docker Desktop.

## Шаг 6: Дополнительно

- **Статистика**: `curl -X GET "http://localhost:8000/stats"`
- **Отписка**: `curl -X POST "http://localhost:8000/unsubscribe" -H "Authorization: Bearer <JWT_TOKEN>"`
- **Тесты**: `uv pip install .[dev]` и `uv run pytest`