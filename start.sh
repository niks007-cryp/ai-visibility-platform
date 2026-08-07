#!/bin/bash

set -e

echo "=== AI Visibility Platform — Production Startup ==="
echo "Environment: ${ENVIRONMENT:-development}"
echo "DATABASE_URL=${DATABASE_URL}"
echo "Running Alembic database migrations..."

alembic upgrade head

echo "Migrations complete. Starting API server..."

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
