FROM python:3.9-slim

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy pyproject.toml for dependency installation
COPY pyproject.toml .

# Install dependencies and verify python-multipart
RUN uv pip install --system . && \
    pip show python-multipart || (echo "python-multipart not installed" && exit 1)

# Copy the rest of the code
COPY . .

# Default command (overridden in docker-compose.yaml)
CMD ["uv", "run", "--no-project", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]