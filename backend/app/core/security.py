from datetime import datetime, timedelta, timezone
from jose import jwt
from core.config import settings


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
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm
    )
    
    return encoded_jwt
