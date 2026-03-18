# TaskForge Backend

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-style FastAPI backend for **TaskForge** — tasks, notes, users, and JWT auth. Designed as a reference service for platform engineering, DevSecOps, observability, and GitOps demos.

---

## 1. Overview

**What it does:** Provides a REST API for user registration, login, task CRUD, and note CRUD. All data is user-scoped. Authentication uses JWT access tokens.

**Why it exists:** To serve as a clean, portfolio-friendly reference backend that demonstrates practical platform engineering patterns: centralized config, structured logging, Prometheus metrics, health probes, security scanning, and GitOps-ready deployment metadata.

**Who it's for:** Engineers learning FastAPI, platform/DevSecOps practitioners building demos, and teams needing a lightweight reference backend for tasks and notes.

---

## 2. Features

| Feature | Status |
|---------|--------|
| JWT auth (register, login) | ✅ |
| Task CRUD + status/priority filters | ✅ |
| Note CRUD | ✅ |
| PostgreSQL + Alembic migrations | ✅ |
| Health / readiness probes | ✅ |
| OpenAPI docs (`/docs`, `/redoc`) | ✅ |
| Structured logging + request IDs | ✅ |
| Prometheus metrics (`/metrics`) | ✅ |
| Docker (dev + prod targets) | ✅ |
| Docker Compose (local stack) | ✅ |
| GitHub Actions CI (lint, test, security, SBOM, Docker) | ✅ |
| Pinned workflow actions (full SHA) | ✅ |
| SBOM generation (CycloneDX) | ✅ |
| Production secret validation | ✅ |
| GitOps deployment metadata | ✅ |
| Manual promotion gate (placeholder) | ✅ |
| Build provenance attestation (SLSA-style) | ✅ |

---

## 3. Architecture Overview

```
Client → FastAPI → Middleware (logging, metrics, request ID)
                → Routes → Services → SQLAlchemy → PostgreSQL
```

- **FastAPI app** — `app/main.py` wires routes, middleware, and exception handling.
- **API routes** — Thin handlers in `app/api/routes/`; auth, users, tasks, notes, health.
- **Service layer** — Business logic in `app/services/`; reusable across routes.
- **DB layer** — SQLAlchemy 2.x models, Alembic migrations, session via dependency.
- **Config** — Single source in `app/core/config.py`; env-driven, production validation.

---

## 4. Repo Structure

```
taskforge-backend/
├── app/
│   ├── main.py           # FastAPI app, middleware, exception handler
│   ├── core/             # Config, security, database, logging, metrics
│   ├── api/              # Routes, deps (auth, DB session)
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Business logic
│   └── db/               # Base, mixins
├── alembic/              # Migrations
├── deploy/               # GitOps deployment docs
├── tests/
├── .github/workflows/    # CI
├── Dockerfile            # dev + prod targets
├── docker-compose.yml
└── pyproject.toml
```

---

## 5. Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL (or Docker Compose for DB)

### Setup

```bash
cd taskforge-backend
pip install -e ".[dev]"
cp .env.example .env
# Edit .env: DATABASE_URL, SECRET_KEY (use any value for local dev)
alembic upgrade head
```

### Run

```bash
uvicorn app.main:app --reload --port 8000
```

- **API:** http://localhost:8000  
- **Docs:** http://localhost:8000/docs  
- **Metrics:** http://localhost:8000/metrics  

**Windows:** Use `.\scripts\format.ps1` or `.\scripts\format.bat` (no `make` required).

---

## 6. Docker Usage

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
docker build --target prod -t taskforge-backend:0.1.0 .
docker run -e DATABASE_URL=... -e SECRET_KEY=... -e APP_ENV=production -p 8000:8000 taskforge-backend:0.1.0
```

Use version or commit SHA for tags; avoid `latest`.

---

## 7. Testing and Quality Checks

| Check | Command |
|-------|---------|
| Lint | `ruff check app tests` |
| Format | `ruff format app tests` |
| Fix | `ruff check app tests --fix` then `ruff format app tests` |
| Tests | `pytest tests/ -v` |
| Security | `bandit -r app -c pyproject.toml` |
| Dependencies | `pip-audit --skip-editable --ignore-vuln CVE-2024-23342` |

Tests use SQLite. `conftest.py` sets `DATABASE_URL`, `SECRET_KEY`, `APP_ENV`.

---

## 8. Environment Variables

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
| `IMAGE_TAG` | No | Image tag (set by CI) |

**Local:** `APP_ENV=development`; `DATABASE_URL` defaults to local PostgreSQL; `SECRET_KEY` can be any value (validation only applies in production).

**Production:** Set `APP_ENV=production`, `DATABASE_URL`, and a secure `SECRET_KEY`. Startup fails if `SECRET_KEY` matches a known insecure value.

---

## 9. Security Notes

- **Passwords:** bcrypt hashing, min 8 chars on registration.
- **JWT:** HS256, configurable expiry. Set `SECRET_KEY` via env in production.
- **Secrets:** Never commit `.env`. In production, startup fails if `SECRET_KEY` is a known insecure value.
- **API:** No stack traces to clients. Task/note access is user-scoped.
- **CI:** Bandit (static analysis), pip-audit (dependency vulnerabilities).
- **Supply chain:** Actions pinned by SHA; SBOM generated; Docker image tagged by commit SHA; build provenance attestation for SBOM and build-metadata artifacts.

**Known limitations:** No refresh tokens, rate limiting, or RBAC. Container image signing deferred (requires registry push). See Roadmap.

---

## 10. Observability

| Feature | Implementation |
|---------|----------------|
| **Health** | `/health` — status, version, env, optional git_sha, image_tag |
| **Readiness** | `/ready` — DB connectivity check |
| **Metrics** | `/metrics` — Prometheus: `http_requests_total`, `http_request_duration_seconds`, `http_requests_in_progress` |
| **Structured logging** | JSON in prod, human-readable when DEBUG |
| **Request IDs** | `X-Request-ID` in request/response; accepts client value or generates one; stored in `request.state` |
| **Error visibility** | Unhandled exceptions logged; clients receive generic 500 |

---

## 11. GitOps Readiness

- **Immutable tags:** Use version or commit SHA for images; document in `deploy/README.md`.
- **Config strategy:** Env vars for local, dev, stage, prod; no baked-in secrets.
- **Deployment metadata:** `APP_ENV`, `GIT_SHA`, `IMAGE_TAG` exposed in `/health`.
- **Future:** Helm/Kustomize, ArgoCD, promotion pipelines — see `deploy/README.md`.

---

## 12. CI/CD Overview

GitHub Actions runs on push/PR to `main`:

| Job | Purpose |
|-----|---------|
| **lint** | Ruff check + format; fails if code needs formatting |
| **test** | pytest with SQLite |
| **security** | Bandit, pip-audit |
| **sbom** | CycloneDX SBOM (JSON); uploaded as artifact |
| **docker** | Build prod image; tag with commit SHA; build metadata artifact |
| **promote** | Manual gate (runs on push to main or workflow_dispatch); requires `production` environment approval |

**Supply chain:** All actions pinned by full 40-char SHA. Docker base image pinned. SBOM generated for Python deps. Build provenance attestation for SBOM and build-metadata (SLSA-style, signed via Sigstore; verify with `gh attestation verify`).

**Promotion gate:** Configure `production` environment in repo Settings → Environments with required reviewers. The promote job blocks until approved.

**Artifact traceability:** `build-metadata` artifact contains `git_sha`, `image_tag`, `version`. Use `GIT_SHA` and `IMAGE_TAG` env vars at deploy time.

---

## 13. API Routes

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
| GET | `/health` | Liveness |
| GET | `/ready` | Readiness |
| GET | `/metrics` | Prometheus metrics |

---

## 14. Roadmap

**Planned next:**

- [ ] Refresh tokens
- [ ] Rate limiting
- [ ] RBAC
- [ ] Audit logging
- [ ] Helm/Kustomize manifests
- [ ] ArgoCD integration

**Later:**

- [ ] OpenTelemetry tracing
- [ ] CodeQL, Trivy container scanning
- [ ] Container image attestation (requires registry push; use `attest-build-provenance` with `push-to-registry`)
- [ ] cosign/signing for critical artifacts (optional hardening)

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
