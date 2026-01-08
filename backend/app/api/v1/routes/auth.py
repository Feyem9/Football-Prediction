from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.user import UserCreate, UserResponse, UserLogin, Token
from controllers.auth_controller import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Endpoint pour créer un nouvel utilisateur."""
    return register_user(user_data, db)


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint pour authentifier un utilisateur et obtenir un token JWT.
    
    Le token retourné doit être utilisé dans le header Authorization
    des requêtes suivantes: `Authorization: Bearer <token>`
    """
    return login_user(login_data, db)

