import enum
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class TaskStatus(str, enum.Enum):
    """
    Using str as a mixin makes the enum JSON-serializable and lets you
    compare it directly with plain strings: status == "pending" works.

    Status flow:
        PENDING → RUNNING → COMPLETED
                          → FAILED
        Any status → CANCELLED (if not already terminal)
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # SAEnum stores the enum VALUES (strings) in Postgres.
    # native_enum=False → stores as VARCHAR rather than a Postgres ENUM type,
    # which makes adding new statuses easier (no ALTER TYPE needed).
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, native_enum=False),
        default=TaskStatus.PENDING,
        nullable=False,
        index=True,  # We'll filter by status often — index it.
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SAEnum(TaskPriority, native_enum=False),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )

    # Optional: when this task should be considered past its deadline
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # result stores whatever the task produced (a JSON string, a message, etc.)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Retry tracking — useful for Phase 5 (message queues)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Foreign key — links this task to its owner user.
    # ondelete="SET NULL": if the user is deleted, tasks aren't deleted —
    # they lose their owner reference instead. Good for audit trails.
    owner_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    owner: Mapped["User"] = relationship("User", back_populates="tasks")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} status={self.status}>"
