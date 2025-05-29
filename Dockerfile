FROM python:3.13-slim

# Установка uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Копирование pyproject.toml для установки зависимостей
COPY pyproject.toml .

# Установка зависимостей и проверка python-multipart и aiosmtplib
RUN uv pip install --system . && \
    pip show python-multipart || (echo "python-multipart не установлен" && exit 1) && \
    pip show aiosmtplib || (echo "aiosmtplib не установлен" && exit 1)

# Копирование остального кода
COPY . .

# Команда по умолчанию (переопределяется в docker-compose.yaml)
CMD ["uv", "run", "--no-project", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]