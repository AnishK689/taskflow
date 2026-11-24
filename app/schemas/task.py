from datetime import datetime
from pydantic import BaseModel
from app.models.task import TaskStatus, TaskPriority


# --- Request schemas ---

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_at: datetime | None = None


class TaskUpdate(BaseModel):
    """PATCH semantics — all fields optional."""
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_at: datetime | None = None
    result: str | None = None
    error_message: str | None = None


class TaskStatusUpdate(BaseModel):
    """Convenience schema for just updating status (e.g. a worker reporting completion)."""
    status: TaskStatus
    result: str | None = None
    error_message: str | None = None


# --- Response schemas ---

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_at: datetime | None
    result: str | None
    error_message: str | None
    retry_count: int
    owner_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
