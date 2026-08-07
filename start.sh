#!/bin/bash
# Production startup script.
# Runs Alembic migrations, then starts the API server.
set -e

echo "=== AI Visibility Platform — Production Startup ==="
echo "Environment: ${ENVIRONMENT:-development}"
echo "Running Alembic database migrations..."

alembic upgrade head

echo "Migrations complete. Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
