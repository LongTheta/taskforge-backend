"""Shared service utilities."""

from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

T = TypeVar("T")


def apply_update(db: Session, instance: T, data: BaseModel) -> T:
    """Apply Pydantic update schema to a model instance. Commits and refreshes."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(instance, field, value)
    db.commit()
    db.refresh(instance)
    return instance
