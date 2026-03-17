"""Note CRUD service."""

from sqlalchemy.orm import Session

from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate
from app.services.base import apply_update


def create_note(db: Session, user: User, data: NoteCreate) -> Note:
    """Create a note for the user."""
    note = Note(
        user_id=user.id,
        title=data.title,
        content=data.content,
        tags=data.tags,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_notes(db: Session, user: User) -> list[Note]:
    """List all notes for the user."""
    return db.query(Note).filter(Note.user_id == user.id).order_by(Note.created_at.desc()).all()


def get_note_by_id(db: Session, note_id: int, user: User) -> Note | None:
    """Get a note by ID if it belongs to the user."""
    return db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()


def update_note(db: Session, note: Note, data: NoteUpdate) -> Note:
    """Update a note with partial data."""
    return apply_update(db, note, data)


def delete_note(db: Session, note: Note) -> None:
    """Delete a note."""
    db.delete(note)
    db.commit()
