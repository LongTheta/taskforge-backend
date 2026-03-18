"""Task CRUD routes."""

from fastapi import APIRouter, Query, Request, status

from app.api.deps import CurrentUser, DbSession, or_404
from app.core.audit import audit_log
from app.core.middleware import get_request_id
from app.schemas.task import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate
from app.services.task_service import (
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks,
    update_task,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create(request: Request, data: TaskCreate, current_user: CurrentUser, db: DbSession):
    """Create a new task."""
    task = create_task(db, current_user, data)
    audit_log(
        action="task_created",
        user_id=current_user.id,
        resource_type="task",
        resource_id=task.id,
        success=True,
        request_id=get_request_id(request),
    )
    return task


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    current_user: CurrentUser,
    db: DbSession,
    status: TaskStatus | None = Query(None, description="Filter by status"),
    priority: TaskPriority | None = Query(None, description="Filter by priority"),
):
    """List all tasks for the current user. Optional filters: status, priority."""
    return get_tasks(db, current_user, status=status, priority=priority)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, current_user: CurrentUser, db: DbSession):
    """Get a task by ID."""
    return or_404(get_task_by_id(db, task_id, current_user), "Task")


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task_route(
    request: Request, task_id: int, data: TaskUpdate, current_user: CurrentUser, db: DbSession
):
    """Update a task."""
    task = or_404(get_task_by_id(db, task_id, current_user), "Task")
    result = update_task(db, task, data)
    audit_log(
        action="task_updated",
        user_id=current_user.id,
        resource_type="task",
        resource_id=task.id,
        success=True,
        request_id=get_request_id(request),
    )
    return result


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_route(request: Request, task_id: int, current_user: CurrentUser, db: DbSession):
    """Delete a task."""
    task = or_404(get_task_by_id(db, task_id, current_user), "Task")
    audit_log(
        action="task_deleted",
        user_id=current_user.id,
        resource_type="task",
        resource_id=task.id,
        success=True,
        request_id=get_request_id(request),
    )
    delete_task(db, task)
