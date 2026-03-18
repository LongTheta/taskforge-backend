"""Health, readiness, and metrics endpoints."""

from fastapi import APIRouter
from fastapi.responses import Response
from sqlalchemy import text

from app.api.deps import DbSession
from app.core.config import APP_VERSION, get_settings
from app.core.metrics import get_metrics

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    """Liveness probe - returns 200 if the app is running."""
    settings = get_settings()
    payload: dict = {
        "status": "ok",
        "service": "taskforge-backend",
        "version": APP_VERSION,
        "env": settings.app_env,
    }
    if settings.git_sha:
        payload["git_sha"] = settings.git_sha
    return payload


@router.get("/ready")
def ready(db: DbSession):
    """Readiness probe - returns 200 if the app can serve traffic (DB connected)."""
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "connected"}


@router.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=get_metrics(), media_type="text/plain; charset=utf-8")
