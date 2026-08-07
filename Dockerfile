# Multi-stage production Dockerfile using Python 3.12 & uv
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency definition
COPY pyproject.toml .

# Install project dependencies into virtual environment
RUN uv venv /app/.venv && uv pip install -r pyproject.toml

# Final runtime image
FROM python:3.12-slim AS runner

WORKDIR /app

# Copy virtualenv and application code
COPY --from=builder /app/.venv /app/.venv
COPY . /app/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
