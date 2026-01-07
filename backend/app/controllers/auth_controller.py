import bcrypt
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User
from schemas.user import UserCreate


def hash_password(password: str) -> str:
    """Hash un mot de passe avec bcrypt."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash."""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def register_user(user_data: UserCreate, db: Session) -> User:
    """
    Crée un nouvel utilisateur avec mot de passe hashé.
    
    Args:
        user_data: Données de l'utilisateur à créer
        db: Session de base de données
        
    Returns:
        User: L'utilisateur créé
        
    Raises:
        HTTPException: Si l'email ou username existe déjà
    """
    # Vérifier si l'email existe déjà
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Vérifier si le username existe déjà
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris"
        )
    
    # Créer l'utilisateur avec mot de passe hashé
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_active=True,
        is_superuser=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
