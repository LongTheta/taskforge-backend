# TaskForge Backend
.PHONY: install dev test lint format security migrate up down docker-build

install:
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	ruff check app tests && ruff format --check app tests

format:
	ruff check app tests --fix && ruff format app tests

security:
	bandit -r app -c pyproject.toml && pip-audit

migrate:
	alembic upgrade head

up:
	docker compose up -d db

down:
	docker compose down

docker-build:
	docker build --target prod -t taskforge-backend:prod .
