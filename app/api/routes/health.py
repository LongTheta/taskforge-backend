"""Health and readiness endpoints for deployment."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import DbSession

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    """Liveness probe - returns 200 if the app is running."""
    return {"status": "ok"}


@router.get("/ready")
def ready(db: DbSession):
    """Readiness probe - returns 200 if the app can serve traffic (DB connected)."""
    db.execute(text("SELECT 1"))
    return {"status": "ready"}
