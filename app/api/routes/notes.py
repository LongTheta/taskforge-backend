"""Note CRUD routes."""

from fastapi import APIRouter, Request, status

from app.api.deps import CurrentUser, DbSession, or_404
from app.core.audit import audit_log
from app.core.middleware import get_request_id
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
from app.services.note_service import (
    create_note,
    delete_note,
    get_note_by_id,
    get_notes,
    update_note,
)

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create(request: Request, data: NoteCreate, current_user: CurrentUser, db: DbSession):
    """Create a new note."""
    note = create_note(db, current_user, data)
    audit_log(
        action="note_created",
        user_id=current_user.id,
        resource_type="note",
        resource_id=note.id,
        success=True,
        request_id=get_request_id(request),
    )
    return note


@router.get("", response_model=list[NoteResponse])
def list_notes(current_user: CurrentUser, db: DbSession):
    """List all notes for the current user."""
    return get_notes(db, current_user)


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(note_id: int, current_user: CurrentUser, db: DbSession):
    """Get a note by ID."""
    return or_404(get_note_by_id(db, note_id, current_user), "Note")


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note_route(
    request: Request, note_id: int, data: NoteUpdate, current_user: CurrentUser, db: DbSession
):
    """Update a note."""
    note = or_404(get_note_by_id(db, note_id, current_user), "Note")
    result = update_note(db, note, data)
    audit_log(
        action="note_updated",
        user_id=current_user.id,
        resource_type="note",
        resource_id=note.id,
        success=True,
        request_id=get_request_id(request),
    )
    return result


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note_route(request: Request, note_id: int, current_user: CurrentUser, db: DbSession):
    """Delete a note."""
    note = or_404(get_note_by_id(db, note_id, current_user), "Note")
    audit_log(
        action="note_deleted",
        user_id=current_user.id,
        resource_type="note",
        resource_id=note.id,
        success=True,
        request_id=get_request_id(request),
    )
    delete_note(db, note)
