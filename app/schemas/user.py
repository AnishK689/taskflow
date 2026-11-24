from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


# --- Request schemas (what the client sends) ---

class UserCreate(BaseModel):
    """Used when registering a new user. Password is plain text here —
    the service layer hashes it before writing to DB."""
    email: EmailStr
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores/hyphens allowed)")
        if len(v) < 3 or len(v) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        return v.lower()


class UserUpdate(BaseModel):
    """All fields optional — PATCH semantics: only send what you want to change."""
    email: EmailStr | None = None
    username: str | None = None
    is_active: bool | None = None


# --- Response schemas (what we send back) ---

class UserResponse(BaseModel):
    """Never includes password or hashed_password."""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # from_attributes=True: allows Pydantic to read from SQLAlchemy model
    # attributes (ORM objects), not just dicts.
    model_config = {"from_attributes": True}
