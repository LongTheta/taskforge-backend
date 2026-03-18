# TaskForge Backend

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-style FastAPI backend for **TaskForge** — tasks, notes, users, and auth. Designed as a reference service for platform engineering, GitOps, and observability demos.

---

## What This Service Does

TaskForge Backend provides:

- **Authentication** — User registration, login, JWT access tokens (bcrypt password hashing)
- **Tasks** — Full CRUD with status, priority, due dates, tags; optional filtering
- **Notes** — Full CRUD with content and tags
- **PostgreSQL** — SQLAlchemy 2.x persistence with Alembic migrations

---

## Core Features

| Feature | Status |
|---------|--------|
| JWT auth (register, login) | ✅ Implemented |
| Task CRUD + status/priority filters | ✅ Implemented |
| Note CRUD | ✅ Implemented |
| PostgreSQL + Alembic | ✅ Implemented |
| Health / readiness probes | ✅ Implemented |
| OpenAPI docs (`/docs`, `/redoc`) | ✅ Implemented |
| Structured logging + request IDs | ✅ Implemented |
| Prometheus metrics (`/metrics`) | ✅ Implemented |
| Docker (dev + prod) | ✅ Implemented |
| GitHub Actions CI | ✅ Implemented |

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
- pip or uv

### Setup

```bash
cd taskforge-backend
pip install -e ".[dev]"
cp .env.example .env
# Edit .env: set DATABASE_URL, SECRET_KEY (see Environment Variables)
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
# Or: python -m pytest tests/ -v
```

Tests use SQLite by default. `DATABASE_URL` and `SECRET_KEY` are set in `conftest.py`; override via env if needed.

---

## Docker

### Local dev (DB only)

```bash
docker compose up -d db
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Full stack (DB + backend)

```bash
docker compose up --build
```

Backend at http://localhost:8000.

### Production image

The Dockerfile uses a multi-stage build. Production image excludes dev dependencies:

```bash
docker build --target prod -t taskforge-backend:prod .
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes (prod) | PostgreSQL connection string |
| `SECRET_KEY` | Yes (prod) | JWT signing key. Generate: `openssl rand -hex 32` |
| `JWT_ALGORITHM` | No | Default: HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Default: 30 |
| `DEBUG` | No | Default: false. Enable for verbose logs |
| `LOG_LEVEL` | No | Default: INFO |

**Security:** Never use default `SECRET_KEY` in production. Never commit `.env`.

---

## API Routes

| Method | Endpoint | Description |
|--------|----------|--------------|
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
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe (DB check) |
| GET | `/metrics` | Prometheus metrics |

---

## Observability

- **Request ID** — Each request gets an `X-Request-ID` header. Pass it in requests for correlation; it is returned in responses.
- **Structured logging** — JSON logs (method, path, status, duration, request_id) for Grafana/Loki integration.
- **Prometheus metrics** — `http_requests_total`, `http_request_duration_seconds`, `http_requests_in_progress` at `/metrics`.

---

## Security Notes

- Passwords hashed with bcrypt; minimum 8 characters for registration.
- JWT tokens; set `SECRET_KEY` via env in production.
- Protected routes require `Authorization: Bearer <token>`.
- Task/note access is user-scoped; no cross-user data leakage.
- No stack traces returned to clients in production.

---

## Project Structure

```
taskforge-backend/
├── app/
│   ├── main.py           # FastAPI app, middleware, routes
│   ├── core/             # Config, security, database, logging
│   ├── api/              # Routes, deps
│   ├── models/           # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/         # Business logic
│   └── db/               # Base, mixins, session
├── alembic/
├── tests/
├── .github/workflows/     # CI
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Future Roadmap

**Planned next:**

- [ ] Alembic migration validation in CI
- [ ] Security scanning (e.g. bandit, safety)
- [ ] Refresh tokens
- [ ] Rate limiting
- [ ] Helm/Kustomize manifests
- [ ] ArgoCD integration

**Later:**

- [ ] RBAC
- [ ] OpenTelemetry traces
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

---

## License

MIT — see [LICENSE](LICENSE).
