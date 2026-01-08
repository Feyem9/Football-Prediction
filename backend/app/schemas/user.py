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


class UserResponse(UserBase):
    """Schéma de réponse utilisateur (sans mot de passe)."""
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True

