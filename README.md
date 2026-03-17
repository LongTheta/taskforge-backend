# TaskForge Backend

Production-style FastAPI backend for **TaskForge** — a secure full-stack task and notes platform. This service provides JWT authentication, user-scoped task and note CRUD, PostgreSQL persistence, and deployment-ready health endpoints.

---

## Features

- **Authentication**: User registration, login, JWT access tokens, password hashing (bcrypt)
- **Tasks**: Full CRUD with status, priority, due dates, tags
- **Notes**: Full CRUD with content and tags
- **PostgreSQL**: SQLAlchemy 2.x, Alembic migrations
- **OpenAPI**: Interactive docs at `/docs`, ReDoc at `/redoc`
- **Tests**: Pytest with SQLite for fast local runs
- **Docker**: Dockerfile and Docker Compose for local dev

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Database | PostgreSQL |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Validation | Pydantic v2 |
| Testing | pytest, FastAPI TestClient |

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (or use Docker Compose)
- pip or uv

### 1. Clone and install

```bash
cd taskforge-backend
pip install -e ".[dev]"
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env: set DATABASE_URL, SECRET_KEY
```

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

---

## Docker Compose

```bash
docker compose up -d db
# Wait for DB to be ready, then:
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Or run everything in containers:

```bash
docker compose up --build
```

Backend will be at http://localhost:8000.

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use SQLite by default for speed. Set `DATABASE_URL` and `SECRET_KEY` in the test environment (see `scripts/test.sh`).

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|--------------|
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login, get JWT |
| GET | `/api/v1/users/me` | Current user (auth) |
| POST | `/api/v1/tasks` | Create task |
| GET | `/api/v1/tasks` | List tasks |
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

---

## Project Structure

```
taskforge-backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── core/                # Config, security, database
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/
│   │   ├── deps.py          # Auth, DB, or_404 helper
│   │   └── routes/          # Auth, users, tasks, notes, health
│   ├── services/            # Business logic (base: apply_update)
│   └── db/                  # Base, mixins (TimestampMixin), session
├── alembic/                 # Migrations
├── tests/
├── scripts/
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

---

## Future Roadmap

- [ ] Frontend integration (React/Vue SPA)
- [ ] GitHub Actions CI (lint, test, build)
- [ ] Docker Compose for full stack
- [ ] GitOps deployment (ArgoCD, Kustomize)
- [ ] Policy enforcement hooks (OPA, admission)
- [ ] Refresh tokens
- [ ] Rate limiting
- [ ] Structured logging

---

## License

MIT
