from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatusUpdate, TaskResponse
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    owner_id: int | None = Query(default=None, description="Assign to a user"),
    db: Session = Depends(get_db),
):
    return task_service.create_task(db, payload, owner_id=owner_id)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    skip: int = 0,
    limit: int = 50,
    # Query() lets us add documentation and validation to query params.
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    owner_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    List tasks with optional filters.

    Examples:
      GET /api/v1/tasks?status=pending
      GET /api/v1/tasks?owner_id=3&status=running
    """
    return task_service.get_tasks(
        db, skip=skip, limit=limit, status_filter=status_filter, owner_id=owner_id
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return task_service.get_task(db, task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    return task_service.update_task(db, task_id, payload)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_task_status(task_id: int, payload: TaskStatusUpdate, db: Session = Depends(get_db)):
    """
    Dedicated endpoint for status transitions.
    Enforces the state machine — can't go backwards from terminal states.
    This is the endpoint a background worker will call in Phase 5.
    """
    return task_service.update_task_status(db, task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task_service.delete_task(db, task_id)
