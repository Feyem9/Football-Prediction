from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError, ExpiredSignatureError
from typing import Tuple

from core.config import settings
from core.database import get_db
from models.user import User
from models.token import TokenBlacklist

# Schéma de sécurité Bearer Token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuel à partir du token JWT.
    Vérifie également que le token n'est pas dans la blacklist.
    """
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Vérifier si le token est blacklisté
    if db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token révoqué",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Décoder le token JWT
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        # Vérifier le type de token (doit être access)
        token_type = payload.get("type")
        if token_type != "access":
            raise credentials_exception
        
        # Extraire l'email du token (subject)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception
    
    # Récupérer l'utilisateur depuis la base de données
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte désactivé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_with_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Tuple[User, str]:
    """
    Dépendance pour obtenir l'utilisateur actuel ET le token.
    Utilisé pour le logout afin de blacklister le token.
    """
    user = await get_current_user(credentials, db)
    return user, credentials.credentials


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dépendance pour vérifier que l'utilisateur est un superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits administrateur requis"
        )
    return current_user

