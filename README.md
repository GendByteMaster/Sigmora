# Sigmora Notification Service

Sigmora (Scalable, Intelligent, Modular Notification Architecture) is a robust notification service built with FastAPI, MongoDB, and Celery. It enables users to subscribe/unsubscribe, customize notification preferences (topics, release time, priority, categories), and receive tailored notifications via email. The service is containerized using Docker Compose and leverages `uv` for efficient dependency management and command execution.

**Repository**: [https://github.com/GendByteMaster/](https://github.com/GendByteMaster/)

## Features

- **Subscription Management**: Subscribe or unsubscribe users via REST API.
- **Custom Preferences**: Filter notifications by topics (e.g., tech, sports), priorities (low, medium, high), categories (general, alert, update), and release time.
- **Statistics**: Retrieve the count of active subscribers.
- **Periodic Notifications**: Generate random notifications every 60 seconds using Celery and send them via email.
- **Authentication**: Secure API access with JWT-based authentication.
- **Scalability**: Supports horizontal scaling with MongoDB replication and Celery workers.
- **Containerization**: Deployed with Docker Compose, including FastAPI, MongoDB, Redis, Celery worker, and Celery Beat services.
- **Dependency Management**: Uses `uv` for fast and reproducible dependency installation.
- **Email Notifications**: Send notifications via email using `aiosmtplib`.

## Project Structure

```
sigmora/
├── main.py                # FastAPI application entry point
├── models.py              # Pydantic models for data validation
├── database.py            # MongoDB connection setup
├── auth.py                # JWT authentication and password hashing
├── routes.py              # API endpoints
├── tasks.py               # Celery tasks for notification generation and email sending
├── config.py              # Configuration and environment variables
├── Dockerfile             # Docker image configuration
├── docker-compose.yaml    # Docker Compose configuration
├── pyproject.toml         # Project metadata and dependencies
├── .env.example           # Sample environment variables
├── tests/                 # Test suite
├── README.md              # Project documentation
```

## Prerequisites

- **Docker** and **Docker Compose** (for containerized deployment).
- **Python 3.13** (for local development without Docker).
- **uv** (installed via `pip install uv` for dependency management).
- MongoDB and Redis (managed by Docker Compose in the default setup).

## Setup Instructions

### Using Docker Compose (Recommended)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/GendByteMaster/sigmora.git
   cd sigmora
   ```

2. **Create a `.env` File**:
   Copy `.env.example` to `.env` and set a secure `SECRET_KEY` and SMTP credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env`:
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

3. **Build and Run**:
   ```bash
   docker-compose up --build
   ```
   If errors occur, rebuild without cache:
   ```bash
   docker-compose build --no-cache
   docker-compose up
   ```

4. **Access the API**:
   - API: `http://localhost:8000`
   - Interactive Documentation: `http://localhost:8000/docs`

5. **Stop the Services**:
   ```bash
   docker-compose down
   ```

### Manual Setup (Without Docker)

1. **Install `uv`**:
   ```bash
   pip install uv
   ```

2. **Create a Virtual Environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # Unix/Mac
   .venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**:
   ```bash
   uv pip install .
   ```

4. **Set Environment Variables**:
   Use `.env` or export variables:
   ```bash
   export MONGO_URI=mongodb://localhost:27017
   export CELERY_BROKER_URL=redis://localhost:6379/0
   export SECRET_KEY=your-secure-secret-key
   export SMTP_HOST=smtp.gmail.com
   export SMTP_PORT=587
   export SMTP_USER=your-email@gmail.com
   export SMTP_PASSWORD=your-app-password
   export SMTP_FROM=no-reply@sigmora.com
   ```

5. **Run MongoDB and Redis**:
   Ensure MongoDB and Redis are running locally or provide their connection URIs.

6. **Start the FastAPI Server**:
   ```bash
   uv run uvicorn main:app --host 0.0.0.0 --port 8000
   ```

7. **Start Celery Worker**:
   ```bash
   uv run celery -A tasks worker --loglevel=info --pool=solo
   ```

8. **Start Celery Beat**:
   ```bash
   uv run celery -A tasks beat --loglevel=info
   ```

## API Endpoints

| Endpoint                | Method | Description                              | Authentication |
|-------------------------|--------|------------------------------------------|----------------|
| `/subscribe`            | POST   | Register and subscribe a new user        | None           |
| `/unsubscribe`          | POST   | Unsubscribe the current user             | JWT            |
| `/stats`                | GET    | Get the number of active subscribers     | None           |
| `/preferences`          | POST   | Update user preferences                  | JWT            |
| `/notifications`        | GET    | Get notifications for the current user   | JWT            |
| `/token`                | POST   | Obtain a JWT token for authentication    | None           |

### Example Requests

1. **Subscribe**:
   ```bash
   curl -X POST "http://localhost:8000/subscribe" -H "Content-Type: application/json" -d '{
     "email": "user@example.com",
     "password": "securepassword",
     "subscribed": true,
     "preferences": {"topics": ["tech"], "priority": ["high"], "category": ["alert"]}
   }'
   ```

2. **Get JWT Token**:
   ```bash
   curl -X POST "http://localhost:8000/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=user@example.com&password=securepassword"
   ```

3. **Update Preferences**:
   ```bash
   curl -X POST "http://localhost:8000/preferences" -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{
     "topics": ["tech", "news"],
     "priority": ["high", "medium"],
     "category": ["alert", "update"]
   }'
   ```

4. **Get Notifications**:
   ```bash
   curl -X GET "http://localhost:8000/notifications" -H "Authorization: Bearer <token>"
   ```

## Notification Generation and Sending

- Notifications are generated every 60 seconds by a Celery task (`generate_and_send_notification`).
- Each notification includes random parameters:
  - `topics`: tech, sports, news
  - `priority`: low, medium, high
  - `category`: general, alert, update
  - `release_time`: current timestamp
- Notifications are sent via email to users whose preferences match the parameters and stored in MongoDB with recipient IDs to prevent duplicates.

## Email Notification Setup

1. **Configure SMTP in `.env`**:
   Specify SMTP server details (e.g., Gmail):
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_FROM=no-reply@sigmora.com
   ```
   For Gmail, use an **App Password** (Google Account > Security > App Passwords).

2. **Rebuild the Project**:
   ```bash
   docker-compose build --no-cache
   docker-compose up
   ```

3. **Verify Email Sending**:
   Notifications are sent every 60 seconds. Check Celery logs:
   ```bash
   docker-compose logs celery
   ```
   Expected output:
   ```
   Email successfully sent to user@example.com
   ```

## Development and Testing

1. **Install Development Dependencies**:
   ```bash
   uv pip install .[dev]
   ```

2. **Run Tests**:
   ```bash
   uv run pytest
   ```
   Tests require `pytest`, `pytest-asyncio`, and `httpx` (included in `[tool.uv]` dev-dependencies). Add tests in the `tests/` directory.

3. **Example Test**:
   Create `tests/test_routes.py`:
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
           "preferences": {"topics": ["tech"], "priority": ["high"]}
       })
       assert response.status_code == 200
       assert response.json() == {"message": "Subscribed successfully"}
   ```

## Design Considerations

- **Modularity**: Code is organized into modules (`main`, `models`, `database`, `auth`, `routes`, `tasks`, `config`) for maintainability.
- **Scalability**: MongoDB and Celery support horizontal scaling. Add more Celery workers or MongoDB replicas as needed.
- **Security**: JWT authentication and bcrypt password hashing. Use a secure `SECRET_KEY` in `.env` for production.
- **Reliability**: Docker Compose healthchecks ensure MongoDB and Redis are ready before dependent services start.
- **Data Storage**: MongoDB stores users and notifications in separate collections, with array-based preferences for efficient filtering.
- **Email Notifications**: Asynchronous email sending via `aiosmtplib` for high performance.

## Troubleshooting

- **Missing `python-multipart` Error**: Ensure `python-multipart==0.0.12` is in `pyproject.toml` and rebuild with `docker-compose build --no-cache`. Verify installation: `docker run -it sigmora-api pip show python-multipart`.
- **MongoDB/Redis Not Ready**: Healthchecks ensure services start in order. Check logs: `docker-compose logs mongo` or `docker-compose logs redis`.
- **Build Issues**: Clear cache: `docker-compose build --no-cache`.
- **Authentication Issues**: Ensure `SECRET_KEY` is consistent across services and tokens are valid.
- **Email Sending Errors**: Verify SMTP credentials in `.env`. For Gmail, use an App Password. Test SMTP:
  ```bash
  docker exec -it sigmora-celery-1 python -c "import asyncio, aiosmtplib; from email.mime.text import MIMEText; async def test(): await aiosmtplib.send(MIMEText('Test'), hostname='smtp.gmail.com', port=587, username='your-email@gmail.com', password='your-app-password', use_tls=True, sender='no-reply@sigmora.com', recipients=['test@example.com']); asyncio.run(test())"
  ```
- **Python 3.13 Compatibility**: If dependencies cause errors, update them in `pyproject.toml` (e.g., `motor==3.7.0`) and rebuild.
- **Windows File Sharing**: Ensure Docker Desktop has access to `G:\Repository\Sigmora` in "File Sharing" settings.

## Future Enhancements

- **Rate Limiting**: Add `slowapi` for API rate-limiting.
- **Admin Panel**: Develop a web-based interface for managing users and notifications.
- **Monitoring**: Use Prometheus/Grafana for metrics and logging.
- **Multi-language Support**: Store notification content in multiple languages.

## License

This project is licensed under the MIT License.