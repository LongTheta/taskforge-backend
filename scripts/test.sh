#!/usr/bin/env bash
# Run tests
set -e
cd "$(dirname "$0")/.."

export DATABASE_URL="sqlite:///./test.db"
export SECRET_KEY="test-secret"

echo "Running pytest..."
pytest tests/ -v
