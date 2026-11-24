"""
Service layer: business logic lives here, not in the routes.

Why separate services from routes?
- Routes handle HTTP (status codes, request parsing, response shaping).
- Services handle business rules (validation, DB queries, side effects).
- This makes services testable without spinning up an HTTP server.
"""
import hashlib
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def _hash_password(password: str) -> str:
    """
    Phase 1: simple SHA-256 hash — good enough to learn the pattern.
    Phase 2 (Auth): we'll replace this with bcrypt, which is slow by design
    to resist brute-force attacks. SHA-256 is fast — bad for passwords.
    """
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(db: Session, payload: UserCreate) -> User:
    hashed_pw = _hash_password(payload.password)
    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hashed_pw,
    )
    db.add(user)
    try:
        db.commit()
        # After commit, the ORM object may be in an "expired" state —
        # attributes are cleared and will be lazy-loaded on next access.
        # db.refresh() re-fetches the row so we can return a fully populated object.
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already exists.",
        )
    return user


def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


def get_users(db: Session, skip: int = 0, limit: int = 50) -> list[User]:
    # Always cap limit — never let clients do SELECT * with no bound.
    limit = min(limit, 100)
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    user = get_user(db, user_id)
    # model_dump(exclude_unset=True): only returns fields the client actually sent.
    # This is what makes PATCH work correctly — we don't overwrite fields with None
    # just because the client didn't include them.
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(user, field, value)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already taken.",
        )
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)
    db.delete(user)
    db.commit()
