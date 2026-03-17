"""Note schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Base note schema."""

    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)


class NoteCreate(NoteBase):
    """Note creation schema."""

    pass


class NoteUpdate(BaseModel):
    """Note update schema - all fields optional."""

    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = Field(None, min_length=1)
    tags: list[str] | None = None


class NoteResponse(NoteBase):
    """Note response schema."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
