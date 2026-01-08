from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.user import UserResponse, UserProfileUpdate, MessageResponse
from controllers.profile_controller import (
    get_user_profile,
    update_user_profile,
    upload_user_avatar,
    delete_user_avatar
)
from middleware.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Récupérer le profil complet de l'utilisateur connecté.
    
    🔒 Nécessite un token JWT valide.
    """
    return get_user_profile(current_user)


@router.put("", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mettre à jour le profil (full_name, bio).
    
    🔒 Nécessite un token JWT valide.
    """
    return update_user_profile(profile_data, current_user, db)


@router.post("/avatar", response_model=UserResponse)
async def upload_avatar_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload une photo de profil (avatar).
    
    - Formats acceptés: JPEG, PNG, GIF, WebP
    - Taille max: 5MB
    - L'image sera redimensionnée à 400x400px
    
    🔒 Nécessite un token JWT valide.
    """
    return await upload_user_avatar(file, current_user, db)


@router.delete("/avatar", response_model=MessageResponse)
async def delete_avatar_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Supprimer la photo de profil.
    
    🔒 Nécessite un token JWT valide.
    """
    result = await delete_user_avatar(current_user, db)
    return MessageResponse(**result)
