import bcrypt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from models.user import User
from models.token import RefreshToken, TokenBlacklist
from schemas.user import (
    UserCreate, UserLogin, Token, TokenPair, 
    RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from core.security import (
    create_access_token, create_refresh_token, decode_token,
    generate_reset_token, generate_verification_token
)
from core.config import settings
from core.email import send_reset_password_email, send_verification_email


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


def authenticate_user(email: str, password: str, db: Session) -> User | None:
    """Authentifie un utilisateur par email et mot de passe."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


def login_user(login_data: UserLogin, db: Session) -> TokenPair:
    """
    Connecte un utilisateur et génère access + refresh token.
    """
    user = authenticate_user(login_data.email, login_data.password, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte désactivé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer access token et refresh token
    access_token = create_access_token(data={"sub": user.email})
    refresh_token, expires_at = create_refresh_token(data={"sub": user.email})
    
    # Sauvegarder le refresh token en BDD
    db_refresh_token = RefreshToken(
        token=refresh_token,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


def refresh_access_token(refresh_data: RefreshTokenRequest, db: Session) -> Token:
    """
    Génère un nouveau access token à partir d'un refresh token valide.
    """
    # Décoder le refresh token
    payload = decode_token(refresh_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide"
        )
    
    # Vérifier que le token existe en BDD et n'est pas révoqué
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_data.refresh_token,
        RefreshToken.revoked == False
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token révoqué ou inexistant"
        )
    
    # Vérifier l'utilisateur
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé ou désactivé"
        )
    
    # Générer nouveau access token
    new_access_token = create_access_token(data={"sub": user.email})
    
    return Token(access_token=new_access_token, token_type="bearer")


def logout_user(access_token: str, user: User, db: Session) -> dict:
    """
    Déconnecte l'utilisateur en blacklistant le token et révoquant les refresh tokens.
    """
    # Décoder le token pour obtenir l'expiration
    payload = decode_token(access_token)
    if payload:
        expires_at = datetime.fromtimestamp(payload.get("exp", 0), tz=timezone.utc)
        
        # Ajouter le token à la blacklist
        blacklisted = TokenBlacklist(
            token=access_token,
            expires_at=expires_at
        )
        db.add(blacklisted)
    
    # Révoquer tous les refresh tokens de l'utilisateur
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    
    db.commit()
    
    return {"message": "Déconnexion réussie", "detail": "Tokens révoqués"}


async def forgot_password(email: str, db: Session) -> dict:
    """
    Envoie un email de réinitialisation de mot de passe.
    """
    user = db.query(User).filter(User.email == email).first()
    
    # Ne pas révéler si l'email existe ou non (sécurité)
    if not user:
        return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé"}
    
    # Générer token de reset
    reset_token = generate_reset_token()
    expires = datetime.now(timezone.utc) + timedelta(hours=settings.password_reset_expire_hours)
    
    # Sauvegarder en BDD
    user.password_reset_token = reset_token
    user.password_reset_expires = expires
    db.commit()
    
    # Envoyer email
    await send_reset_password_email(email, reset_token)
    
    return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé"}


def reset_password(reset_data: ResetPasswordRequest, db: Session) -> dict:
    """
    Réinitialise le mot de passe avec le token.
    """
    user = db.query(User).filter(
        User.password_reset_token == reset_data.token,
        User.password_reset_expires > datetime.now(timezone.utc)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token invalide ou expiré"
        )
    
    # Mettre à jour le mot de passe
    user.hashed_password = hash_password(reset_data.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None
    
    # Révoquer tous les refresh tokens (forcer reconnexion)
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    
    db.commit()
    
    return {"message": "Mot de passe réinitialisé avec succès"}


def verify_email_token(token: str, db: Session) -> dict:
    """
    Vérifie l'email de l'utilisateur avec le token.
    """
    user = db.query(User).filter(User.email_verification_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de vérification invalide"
        )
    
    user.email_verified = True
    user.email_verification_token = None
    db.commit()
    
    return {"message": "Email vérifié avec succès"}


async def register_user(user_data: UserCreate, db: Session) -> User:
    """
    Crée un nouvel utilisateur avec mot de passe hashé et envoie email de vérification.
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
    
    # Générer token de vérification email
    verification_token = generate_verification_token()
    
    # Créer l'utilisateur avec mot de passe hashé
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_active=True,
        is_superuser=False,
        email_verified=False,
        email_verification_token=verification_token
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Envoyer email de vérification
    await send_verification_email(new_user.email, verification_token)
    
    return new_user


def is_token_blacklisted(token: str, db: Session) -> bool:
    """Vérifie si un token est dans la blacklist."""
    return db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first() is not None


