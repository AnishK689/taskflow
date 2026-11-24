from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate

# Terminal statuses — once here, a task can't transition back.
TERMINAL_STATUSES = {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}


def create_task(db: Session, payload: TaskCreate, owner_id: int | None = None) -> Task:
    task = Task(**payload.model_dump(), owner_id=owner_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return task


def get_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    status_filter: TaskStatus | None = None,
    owner_id: int | None = None,
) -> list[Task]:
    limit = min(limit, 100)
    query = select(Task)

    # Build filters dynamically — only add clauses for provided params.
    # This avoids ugly if/else chains and is easy to extend.
    if status_filter:
        query = query.where(Task.status == status_filter)
    if owner_id is not None:
        query = query.where(Task.owner_id == owner_id)

    query = query.offset(skip).limit(limit)
    return list(db.execute(query).scalars().all())


def update_task(db: Session, task_id: int, payload: TaskUpdate) -> Task:
    task = get_task(db, task_id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def update_task_status(db: Session, task_id: int, payload: TaskStatusUpdate) -> Task:
    """
    Explicit status-transition endpoint used by workers (Phase 5).
    Enforces the state machine: you can't transition out of a terminal status.
    """
    task = get_task(db, task_id)

    if task.status in TERMINAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Task is already in terminal status '{task.status}'. Cannot transition.",
        )

    task.status = payload.status
    if payload.result is not None:
        task.result = payload.result
    if payload.error_message is not None:
        task.error_message = payload.error_message

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> None:
    task = get_task(db, task_id)
    db.delete(task)
    db.commit()
