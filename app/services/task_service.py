"""Task CRUD service."""

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.base import apply_update


def create_task(db: Session, user: User, data: TaskCreate) -> Task:
    """Create a task for the user."""
    task = Task(
        user_id=user.id,
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        due_date=data.due_date,
        tags=data.tags,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks(db: Session, user: User) -> list[Task]:
    """List all tasks for the user."""
    return db.query(Task).filter(Task.user_id == user.id).order_by(Task.created_at.desc()).all()


def get_task_by_id(db: Session, task_id: int, user: User) -> Task | None:
    """Get a task by ID if it belongs to the user."""
    return db.query(Task).filter(Task.id == task_id, Task.user_id == user.id).first()


def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    """Update a task with partial data."""
    return apply_update(db, task, data)


def delete_task(db: Session, task: Task) -> None:
    """Delete a task."""
    db.delete(task)
    db.commit()
