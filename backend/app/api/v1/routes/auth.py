from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.user import UserCreate, UserResponse
from controllers.auth_controller import register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Endpoint pour créer un nouvel utilisateur."""
    return register_user(user_data, db)
