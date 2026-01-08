from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Tuple

from core.database import get_db
from schemas.user import (
    UserCreate, UserResponse, UserLogin, Token, TokenPair,
    RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest, MessageResponse
)
from controllers.auth_controller import (
    register_user, login_user, refresh_access_token, logout_user,
    forgot_password, reset_password, verify_email_token
)
from middleware.auth import get_current_user, get_current_user_with_token
from models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Créer un nouveau compte utilisateur.
    Un email de vérification sera envoyé.
    """
    return await register_user(user_data, db)


@router.post("/login", response_model=TokenPair)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authentifier un utilisateur et obtenir un access token + refresh token.
    
    - **access_token** : Token JWT valide 30 minutes
    - **refresh_token** : Token pour renouveler l'access token (7 jours)
    """
    return login_user(login_data, db)


@router.post("/refresh", response_model=Token)
def refresh(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Renouveler l'access token avec un refresh token valide.
    """
    return refresh_access_token(refresh_data, db)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Retourne les informations de l'utilisateur actuellement connecté.
    
    🔒 Nécessite un token JWT valide.
    """
    return current_user


@router.post("/logout", response_model=MessageResponse)
async def logout(
    user_and_token: Tuple[User, str] = Depends(get_current_user_with_token),
    db: Session = Depends(get_db)
):
    """
    Déconnexion de l'utilisateur.
    Blackliste le token actuel et révoque tous les refresh tokens.
    
    🔒 Nécessite un token JWT valide.
    """
    user, token = user_and_token
    result = logout_user(token, user, db)
    return MessageResponse(**result)


@router.post("/forgot-password", response_model=MessageResponse)
async def request_forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Demander un email de réinitialisation de mot de passe.
    
    Par sécurité, la réponse sera identique que l'email existe ou non.
    """
    result = await forgot_password(data.email, db)
    return MessageResponse(**result)


@router.post("/reset-password", response_model=MessageResponse)
def do_reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Réinitialiser le mot de passe avec le token reçu par email.
    """
    result = reset_password(data, db)
    return MessageResponse(**result)


@router.get("/verify-email/{token}", response_model=MessageResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Vérifier l'adresse email avec le token reçu lors de l'inscription.
    """
    result = verify_email_token(token, db)
    return MessageResponse(**result)



