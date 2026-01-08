from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from core.config import settings
import secrets


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Crée un token JWT signé.
    
    Args:
        data: Données à encoder dans le token (ex: {"sub": user_email})
        expires_delta: Durée de validité du token (optionnel)
        
    Returns:
        Token JWT encodé
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> tuple[str, datetime]:
    """
    Crée un refresh token JWT avec une expiration longue.
    
    Args:
        data: Données à encoder dans le token
        
    Returns:
        Tuple (token_encodé, date_expiration)
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt, expire


def decode_token(token: str) -> dict | None:
    """
    Décode un token JWT.
    
    Args:
        token: Token JWT à décoder
        
    Returns:
        Payload du token ou None si invalide
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


def generate_reset_token() -> str:
    """Génère un token unique pour le reset de mot de passe."""
    return secrets.token_urlsafe(32)


def generate_verification_token() -> str:
    """Génère un token unique pour la vérification d'email."""
    return secrets.token_urlsafe(32)

