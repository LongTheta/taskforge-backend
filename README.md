# TaskForge Backend

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A clean, production-style FastAPI backend for **TaskForge** — tasks, notes, users, and auth. Designed as a reference service for platform engineering, GitOps, and observability demos.

---

## What This Service Does

- **Authentication** — User registration, login, JWT access tokens (bcrypt)
- **Tasks** — Full CRUD with status, priority, due dates, tags; optional filtering
- **Notes** — Full CRUD with content and tags
- **PostgreSQL** — SQLAlchemy 2.x persistence with Alembic migrations

---

## Implemented Features

| Feature | Status |
|---------|--------|
| JWT auth (register, login) | ✅ |
| Task CRUD + status/priority filters | ✅ |
| Note CRUD | ✅ |
| PostgreSQL + Alembic | ✅ |
| Health / readiness probes | ✅ |
| OpenAPI docs (`/docs`, `/redoc`) | ✅ |
| Structured logging + request IDs | ✅ |
| Prometheus metrics (`/metrics`) | ✅ |
| Docker (dev + prod targets) | ✅ |
| GitHub Actions CI (lint, test, security, Docker) | ✅ |

---

## Architecture

```
Client → FastAPI → Middleware (logging, metrics, request ID)
                → Routes → Services → SQLAlchemy → PostgreSQL
```

---

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL (or Docker Compose for DB)

### Setup

```bash
cd taskforge-backend
pip install -e ".[dev]"
cp .env.example .env
# Edit .env: DATABASE_URL, SECRET_KEY
alembic upgrade head
```

### Run

```bash
uvicorn app.main:app --reload --port 8000
# Or: make dev
```

- **API:** http://localhost:8000  
- **Docs:** http://localhost:8000/docs  
- **Metrics:** http://localhost:8000/metrics  

---

## Testing

```bash
pytest tests/ -v
# Or: make test
```

Tests use SQLite. `conftest.py` sets `DATABASE_URL`, `SECRET_KEY`, `APP_ENV`.

---

## Lint, Format, Security

```bash
make lint      # Ruff check and format check
make format    # Ruff fix and format
make security  # Bandit and pip-audit
```

---

## Docker

### Local dev (DB only)

```bash
docker compose up -d db
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Full stack

```bash
docker compose up --build
```

### Production image

```bash
docker build --target prod -t taskforge-backend:prod .
# Or: make docker-build
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_ENV` | No | `development` \| `production` \| `test`. Default: development |
| `DATABASE_URL` | Yes (prod) | PostgreSQL connection string |
| `SECRET_KEY` | Yes (prod) | JWT signing key. Generate: `openssl rand -hex 32` |
| `JWT_ALGORITHM` | No | Default: HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Default: 30 |
| `DEBUG` | No | Default: false |
| `LOG_LEVEL` | No | Default: INFO |
| `GIT_SHA` | No | Build metadata (set by CI) |

**Security:** In production, set `APP_ENV=production`, `DATABASE_URL`, and `SECRET_KEY`. Never commit `.env`.

---

## API Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login, get JWT |
| GET | `/api/v1/users/me` | Current user (auth) |
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks` | List tasks (`?status=`, `?priority=`) |
| GET | `/api/v1/tasks/{id}` | Get task |
| PATCH | `/api/v1/tasks/{id}` | Update task |
| DELETE | `/api/v1/tasks/{id}` | Delete task |
| POST | `/api/v1/notes` | Create note |
| GET | `/api/v1/notes` | List notes |
| GET | `/api/v1/notes/{id}` | Get note |
| PATCH | `/api/v1/notes/{id}` | Update note |
| DELETE | `/api/v1/notes/{id}` | Delete note |
| GET | `/health` | Liveness (version, env, optional git_sha) |
| GET | `/ready` | Readiness (DB check) |
| GET | `/metrics` | Prometheus metrics |

---

## Auth Overview

- Register: `POST /api/v1/auth/register` with `email`, `password` (min 8 chars)
- Login: `POST /api/v1/auth/login` → returns `access_token`
- Protected routes: `Authorization: Bearer <token>`
- Task/note access is user-scoped

---

## Observability

- **Request ID** — `X-Request-ID` header on requests and responses
- **Structured logging** — JSON logs (method, path, status, duration, request_id)
- **Prometheus** — `http_requests_total`, `http_request_duration_seconds`, `http_requests_in_progress` at `/metrics`

---

## CI Overview

GitHub Actions runs on push/PR to main:

- **lint** — Ruff check + format
- **test** — pytest
- **security** — Bandit, pip-audit
- **docker** — Build prod image

---

## Security Notes

- Passwords: bcrypt, min 8 chars. JWT: set `SECRET_KEY` via env in production.
- No stack traces to clients. Task/note access user-scoped.
- CI runs Bandit and pip-audit.

---

## Repo Structure

```
taskforge-backend/
├── app/
│   ├── main.py           # FastAPI app, middleware, exception handler
│   ├── core/             # Config, security, database, logging, metrics
│   ├── api/              # Routes, deps
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── db/               # Base, mixins
├── alembic/
├── tests/
├── .github/workflows/    # CI
├── Dockerfile            # dev + prod targets
├── docker-compose.yml
└── pyproject.toml
```

---

## Roadmap

**Planned next:**

- [ ] Alembic migration validation in CI
- [ ] Refresh tokens
- [ ] Rate limiting
- [ ] Helm/Kustomize manifests
- [ ] ArgoCD integration

**Later:**

- [ ] RBAC
- [ ] OpenTelemetry traces
- [ ] CodeQL, Trivy
- [ ] Frontend integration

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Database | PostgreSQL |
| Auth | JWT (python-jose), bcrypt |
| Validation | Pydantic v2 |
| Metrics | prometheus_client |
| Testing | pytest, FastAPI TestClient |
| Lint | Ruff |
| Security | Bandit, pip-audit |

---

## License

MIT — see [LICENSE](LICENSE).
