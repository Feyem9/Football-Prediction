from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    """Schéma de base pour l'utilisateur."""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schéma pour la création d'utilisateur (avec mot de passe)."""
    password: str


class UserLogin(BaseModel):
    """Schéma pour la connexion utilisateur."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schéma pour la réponse de token JWT."""
    access_token: str
    token_type: str = "bearer"


class TokenPair(BaseModel):
    """Schéma pour la réponse avec access et refresh token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Schéma pour la demande de refresh token."""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Schéma pour la demande de reset de mot de passe."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schéma pour la réinitialisation de mot de passe."""
    token: str
    new_password: str


class UserResponse(UserBase):
    """Schéma de réponse utilisateur (sans mot de passe)."""
    id: int
    is_active: bool = True
    is_superuser: bool = False
    email_verified: Optional[bool] = False
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Schéma pour la mise à jour du profil."""
    full_name: Optional[str] = None
    bio: Optional[str] = None


class MessageResponse(BaseModel):
    """Schéma pour les réponses simples."""
    message: str
    detail: Optional[str] = None



