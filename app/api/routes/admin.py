"""Admin routes. Requires admin role."""

from typing import Annotated

from fastapi import APIRouter

from app.api.deps import DbSession, require_role
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    current_user: Annotated[User, require_role("admin")],
    db: DbSession,
):
    """Admin-only: basic stats. Requires admin role."""
    from sqlalchemy import func

    from app.models.note import Note
    from app.models.task import Task

    user_count = db.query(func.count(User.id)).scalar() or 0
    task_count = db.query(func.count(Task.id)).scalar() or 0
    note_count = db.query(func.count(Note.id)).scalar() or 0
    return {
        "users": user_count,
        "tasks": task_count,
        "notes": note_count,
    }
