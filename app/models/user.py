from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    # Mapped[type] is SQLAlchemy 2.0's typed column syntax.
    # It lets Python type checkers understand your model attributes.
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # timezone-aware UTC timestamps: always store UTC in the DB.
    # Never store local time — it makes queries and comparisons a nightmare.
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

    # One user can have many tasks. back_populates wires the reverse
    # relationship on Task.owner so both sides stay in sync in memory.
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="owner")  # noqa: F821

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
