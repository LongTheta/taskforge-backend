"""Task CRUD routes."""

from typing import Literal

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession, or_404
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import (
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks,
    update_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])

TaskStatusFilter = Literal["todo", "in_progress", "done"]
TaskPriorityFilter = Literal["low", "medium", "high"]


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create(data: TaskCreate, current_user: CurrentUser, db: DbSession):
    """Create a new task."""
    return create_task(db, current_user, data)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    current_user: CurrentUser,
    db: DbSession,
    status: TaskStatusFilter | None = Query(None, description="Filter by status"),
    priority: TaskPriorityFilter | None = Query(None, description="Filter by priority"),
):
    """List all tasks for the current user. Optional filters: status, priority."""
    return get_tasks(db, current_user, status=status, priority=priority)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, current_user: CurrentUser, db: DbSession):
    """Get a task by ID."""
    return or_404(get_task_by_id(db, task_id, current_user), "Task")


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task_route(task_id: int, data: TaskUpdate, current_user: CurrentUser, db: DbSession):
    """Update a task."""
    task = or_404(get_task_by_id(db, task_id, current_user), "Task")
    return update_task(db, task, data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_route(task_id: int, current_user: CurrentUser, db: DbSession):
    """Delete a task."""
    task = or_404(get_task_by_id(db, task_id, current_user), "Task")
    delete_task(db, task)
