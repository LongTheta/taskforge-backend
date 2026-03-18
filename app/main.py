"""TaskForge FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import auth, health, notes, tasks, users
from app.core.config import APP_VERSION, get_settings
from app.core.logging_config import configure_logging
from app.core.middleware import REQUEST_ID_HEADER, RequestLoggingMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: configure logging, validate production secrets."""
    configure_logging()
    settings = get_settings()
    settings.validate_production()
    version = settings.app_version or APP_VERSION
    sha = settings.git_sha or "unknown"
    logger.info(
        "Starting TaskForge Backend | env=%s version=%s sha=%s",
        settings.app_env,
        version,
        sha,
        extra={"version": version, "env": settings.app_env, "git_sha": sha},
    )
    yield


app = FastAPI(
    title="TaskForge API",
    description="Secure task and notes platform backend. JWT auth, task/note CRUD, PostgreSQL.",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "auth", "description": "Authentication (register, login)"},
        {"name": "users", "description": "Current user profile"},
        {"name": "tasks", "description": "Task CRUD with status/priority"},
        {"name": "notes", "description": "Note CRUD"},
        {"name": "health", "description": "Liveness, readiness, info, metrics"},
    ],
)

app.add_middleware(RequestLoggingMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Log unhandled exceptions; return safe 500 (no stack trace). Include X-Request-ID."""
    request_id = getattr(request.state, "request_id", None)
    logger.exception(
        "Unhandled exception: %s",
        exc,
        extra={"request_id": request_id} if request_id else {},
    )
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
    if request_id:
        response.headers[REQUEST_ID_HEADER] = request_id
    return response


app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")
