# Sigmora Notification Service

Sigmora (Scalable, Intelligent, Modular Notification Architecture) — это масштабируемый сервис уведомлений, построенный на FastAPI, MongoDB и Celery. Он позволяет пользователям подписываться и отписываться от уведомлений, настраивать предпочтения (темы, время отправки, приоритет, категории) и получать персонализированные уведомления. Сервис контейнеризован с помощью Docker Compose и использует `uv` для эффективного управления зависимостями и выполнения команд.

**Репозиторий**: [https://github.com/GendByteMaster/](https://github.com/GendByteMaster/)

## Возможности

- **Управление подпиской**: Подписка и отписка пользователей через REST API.
- **Настраиваемые предпочтения**: Фильтрация уведомлений по темам (например, технологии, спорт), приоритетам (низкий, средний, высокий), категориям (общее, оповещение, обновление) и времени отправки.
- **Статистика**: Получение количества активных подписчиков.
- **Периодические уведомления**: Генерация случайных уведомлений каждые 60 секунд с помощью Celery.
- **Аутентификация**: Безопасный доступ к API с использованием JWT.
- **Масштабируемость**: Поддержка горизонтального масштабирования с репликацией MongoDB и воркерами Celery.
- **Контейнеризация**: Развертывание с Docker Compose, включая сервисы FastAPI, MongoDB, Redis, Celery worker и Celery Beat.
- **Управление зависимостями**: Использование `uv` для быстрой и воспроизводимой установки зависимостей.

## Структура проекта

```
sigmora/
├── main.py                # Точка входа приложения FastAPI
├── models.py              # Модели Pydantic для валидации данных
├── database.py            # Настройка подключения к MongoDB
├── auth.py                # Аутентификация JWT и хеширование паролей
├── routes.py              # Эндпоинты API
├── tasks.py               # Задачи Celery для генерации уведомлений
├── config.py              # Конфигурация и переменные окружения
├── Dockerfile             # Конфигурация Docker-образа
├── docker-compose.yaml    # Конфигурация Docker Compose
├── pyproject.toml         # Метаданные проекта и зависимости
├── .env.example           # Пример переменных окружения
├── tests/                 # Набор тестов
├── README.md              # Документация проекта
```

## Требования

- **Docker** и **Docker Compose** (для контейнеризированного развертывания).
- **Python 3.9+** (для локальной разработки без Docker).
- **uv** (устанавливается через `pip install uv` для управления зависимостями).
- MongoDB и Redis (управляются Docker Compose в стандартной конфигурации).

## Инструкции по установке

### Использование Docker Compose (рекомендуется)

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/GendByteMaster/sigmora.git
   cd sigmora
   ```

2. **Создайте файл `.env`**:
   Скопируйте `.env.example` в `.env` и задайте безопасный `SECRET_KEY`:
   ```bash
   cp .env.example .env
   ```
   Отредактируйте `.env`:
   ```env
   SECRET_KEY=your-secure-secret-key
   MONGO_URI=mongodb://mongo:27017
   CELERY_BROKER_URL=redis://redis:6379/0
   ```

3. **Соберите и запустите**:
   ```bash
   docker-compose up --build
   ```
   Если возникают ошибки, пересоберите без кэша:
   ```bash
   docker-compose build --no-cache
   docker-compose up
   ```

4. **Доступ к API**:
   - API: `http://localhost:8000`
   - Интерактивная документация: `http://localhost:8000/docs`

5. **Остановка сервисов**:
   ```bash
   docker-compose down
   ```

### Ручная установка (без Docker)

1. **Установите `uv`**:
   ```bash
   pip install uv
   ```

2. **Создайте виртуальное окружение**:
   ```bash
   uv venv
   source .venv/bin/activate  # Unix/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Установите зависимости**:
   ```bash
   uv pip install .
   ```

4. **Задайте переменные окружения**:
   Используйте `.env` или экспортируйте переменные:
   ```bash
   export MONGO_URI=mongodb://localhost:27017
   export CELERY_BROKER_URL=redis://localhost:6379/0
   export SECRET_KEY=your-secure-secret-key
   ```

5. **Запустите MongoDB и Redis**:
   Убедитесь, что MongoDB и Redis запущены локально или предоставьте их URI подключения.

6. **Запустите сервер FastAPI**:
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port 8000
   ```

7. **Запустите воркер Celery**:
   ```bash
   uv run celery -A tasks worker --loglevel=info --pool=solo
   ```

8. **Запустите планировщик Celery Beat**:
   ```bash
   uv run celery -A tasks beat --loglevel=info
   ```

## Эндпоинты API

| Эндпоинт                | Метод | Описание                                 | Аутентификация |
|-------------------------|-------|------------------------------------------|----------------|
| `/subscribe`            | POST  | Регистрация и подписка нового пользователя | Нет            |
| `/unsubscribe`          | POST  | Отписка текущего пользователя            | JWT            |
| `/stats`                | GET   | Получение количества активных подписчиков | Нет            |
| `/preferences`          | POST  | Обновление предпочтений пользователя      | JWT            |
| `/notifications`        | GET   | Получение уведомлений для пользователя    | JWT            |
| `/token`                | POST  | Получение JWT-токена для аутентификации   | Нет            |

### Примеры запросов

1. **Подписка**:
   ```bash
   curl -X POST "http://localhost:8000/subscribe" -H "Content-Type: application/json" -d '{
     "email": "user@example.com",
     "password": "securepassword",
     "subscribed": true,
     "preferences": {"topic": ["tech"], "priority": ["high"], "category": ["alert"]}
   }'
   ```

2. **Получение JWT-токена**:
   ```bash
   curl -X POST "http://localhost:8000/token" -d "username=user@example.com&password=securepassword"
   ```

3. **Обновление предпочтений**:
   ```bash
   curl -X POST "http://localhost:8000/preferences" -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{
     "topic": ["tech", "news"],
     "priority": ["high", "medium"],
     "category": ["alert", "update"]
   }'
   ```

4. **Получение уведомлений**:
   ```bash
   curl -X GET "http://localhost:8000/notifications" -H "Authorization: Bearer <token>"
   ```

## Генерация уведомлений

- Уведомления генерируются каждые 60 секунд задачей Celery (`generate_and_send_notification`).
- Каждое уведомление содержит случайные параметры:
  - `topic`: технологии, спорт, новости
  - `priority`: низкий, средний, высокий
  - `category`: общее, оповещение, обновление
  - `release_time`: текущая метка времени
- Уведомления отправляются пользователям, чьи предпочтения соответствуют параметрам, и сохраняются в MongoDB с идентификаторами получателей для предотвращения дублирования.

## Разработка и тестирование

1. **Установите зависимости для разработки**:
   ```bash
   uv pip install .[dev]
   ```

2. **Запустите тесты**:
   ```bash
   uv run pytest
   ```
   Тесты требуют `pytest`, `pytest-asyncio` и `httpx` (включены в `[tool.uv]` dev-dependencies). Добавляйте тесты в директорию `tests/`.

3. **Пример теста**:
   Создайте файл `tests/test_routes.py`:
   ```python
   import pytest
   from fastapi.testclient import TestClient
   from main import app

   client = TestClient(app)

   @pytest.mark.asyncio
   async def test_subscribe():
       response = client.post("/subscribe", json={
           "email": "test@example.com",
           "password": "testpassword",
           "subscribed": True,
           "preferences": {"topic": ["tech"], "priority": ["high"]}
       })
       assert response.status_code == 200
       assert response.json() == {"message": "Subscribed successfully"}
   ```

## Особенности проектирования

- **Модульность**: Код разделен на модули (`main`, `models`, `database`, `auth`, `routes`, `tasks`, `config`) для удобства поддержки.
- **Масштабируемость**: MongoDB и Celery поддерживают горизонтальное масштабирование. Добавляйте воркеры Celery или реплики MongoDB по мере необходимости.
- **Безопасность**: JWT-аутентификация и хеширование паролей с помощью bcrypt. Используйте безопасный `SECRET_KEY` в `.env` для продакшена.
- **Надежность**: Healthchecks в `docker-compose.yaml` гарантируют готовность MongoDB и Redis перед запуском зависимых сервисов.
- **Хранение данных**: MongoDB хранит пользователей и уведомления в отдельных коллекциях с массивом предпочтений для эффективной фильтрации.

## Устранение неполадок

- **Ошибка `python-multipart`**: Убедитесь, что в `pyproject.toml` указан `python-multipart==0.0.12`, и пересоберите с `docker-compose build --no-cache`. Проверьте установку: `docker run -it sigmora-api pip show python-multipart`.
- **MongoDB/Redis не готовы**: Healthchecks обеспечивают правильный порядок запуска. Проверьте логи: `docker-compose logs mongo` или `docker-compose logs redis`.
- **Проблемы сборки**: Очистите кэш: `docker-compose build --no-cache`.
- **Ошибки аутентификации**: Убедитесь, что `SECRET_KEY` одинаков для всех сервисов и токены действительны.
- **Файловая система Windows**: Убедитесь, что Docker Desktop имеет доступ к `G:\Repository\Sigmora` в настройках "Общий доступ к файлам".

## Планы на будущее

- **Ограничение скорости**: Добавить `slowapi` для ограничения скорости API.
- **Уведомления по email**: Интеграция с SendGrid для отправки email.
- **Админ-панель**: Разработка веб-интерфейса для управления пользователями и уведомлениями.
- **Мониторинг**: Использование Prometheus/Grafana для метрик и логирования.
- **Поддержка нескольких языков**: Хранение содержимого уведомлений на разных языках.

## Лицензия

Проект распространяется под лицензией MIT.