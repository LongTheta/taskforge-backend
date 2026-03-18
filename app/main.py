"""TaskForge FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import auth, health, notes, tasks, users
from app.core.logging_config import configure_logging
from app.core.middleware import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    configure_logging()
    from app.core.config import get_settings

    settings = get_settings()
    if not settings.debug and settings.secret_key in (
        "change-me-in-production",
        "your-secret-key-change-in-production",
    ):
        logging.getLogger(__name__).warning(
            "SECRET_KEY appears to be default. Set SECRET_KEY in production."
        )
    yield


app = FastAPI(
    title="TaskForge API",
    description="Secure task and notes platform backend. JWT auth, task/note CRUD, PostgreSQL.",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "auth", "description": "Authentication (register, login)"},
        {"name": "users", "description": "Current user profile"},
        {"name": "tasks", "description": "Task CRUD with status/priority"},
        {"name": "notes", "description": "Note CRUD"},
        {"name": "health", "description": "Liveness, readiness, metrics"},
    ],
)

app.add_middleware(RequestLoggingMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Log unhandled exceptions and return safe error response."""
    logger = logging.getLogger(__name__)
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Routes
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")
