# TaskForge Backend - Common commands
.PHONY: install dev test lint format migrate up down

install:
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	ruff check app tests
	ruff format --check app tests

format:
	ruff check app tests --fix
	ruff format app tests

migrate:
	alembic upgrade head

up:
	docker compose up -d db

down:
	docker compose down
