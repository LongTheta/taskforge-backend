"""Task schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

TaskStatus = Literal["todo", "in_progress", "done"]
TaskPriority = Literal["low", "medium", "high"]


class TaskBase(BaseModel):
    """Base task schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    due_date: date | None = None
    tags: list[str] = Field(default_factory=list)


class TaskCreate(TaskBase):
    """Task creation schema."""

    pass


class TaskUpdate(BaseModel):
    """Task update schema - all fields optional."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    tags: list[str] | None = None


class TaskResponse(TaskBase):
    """Task response schema."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
