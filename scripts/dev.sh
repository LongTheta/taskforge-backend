#!/usr/bin/env bash
# Local development - run migrations and start server
set -e
cd "$(dirname "$0")/.."

echo "Running migrations..."
alembic upgrade head

echo "Starting uvicorn..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
