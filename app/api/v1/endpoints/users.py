from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services import user_service

# APIRouter lets us group related routes, then include them in main app.
# prefix="/users" means all routes here are under /api/v1/users/...
router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    201 Created is more accurate than 200 OK when you've created a resource.
    """
    return user_service.create_user(db, payload)


@router.get("/", response_model=list[UserResponse])
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all users with pagination. skip/limit come from query params."""
    return user_service.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Fetch a single user by ID. Returns 404 if not found."""
    return user_service.get_user(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    """
    Partial update (PATCH). Only fields you send are changed.
    If you want to replace the entire resource, that's PUT — but PATCH
    is almost always the right choice for APIs.
    """
    return user_service.update_user(db, user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user. 204 No Content = success, nothing to return.
    Note: their tasks' owner_id will be set to NULL (see FK definition).
    """
    user_service.delete_user(db, user_id)
