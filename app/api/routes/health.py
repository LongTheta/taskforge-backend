"""Health, readiness, and metrics endpoints."""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.core.metrics import get_metrics

router = APIRouter(tags=["health"])

SERVICE_VERSION = "0.1.0"


@router.get("/health")
def health():
    """Liveness probe - returns 200 if the app is running."""
    return {"status": "ok", "service": "taskforge-backend", "version": SERVICE_VERSION}


@router.get("/ready")
def ready(db: DbSession):
    """Readiness probe - returns 200 if the app can serve traffic (DB connected)."""
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "connected"}


@router.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=get_metrics(), media_type="text/plain; charset=utf-8")
