from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from models.user import User
from schemas.user import UserProfileUpdate
from core.cloudinary_service import upload_avatar, delete_avatar


def get_user_profile(user: User) -> User:
    """
    Récupère le profil complet de l'utilisateur.
    """
    return user


def update_user_profile(
    profile_data: UserProfileUpdate,
    user: User,
    db: Session
) -> User:
    """
    Met à jour le profil de l'utilisateur.
    """
    if profile_data.full_name is not None:
        user.full_name = profile_data.full_name
    
    if profile_data.bio is not None:
        # Limiter la bio à 500 caractères
        user.bio = profile_data.bio[:500]
    
    db.commit()
    db.refresh(user)
    
    return user


async def upload_user_avatar(
    file: UploadFile,
    user: User,
    db: Session
) -> User:
    """
    Upload une photo de profil sur Cloudinary.
    """
    # Upload sur Cloudinary
    avatar_url = await upload_avatar(file, user.id)
    
    # Sauvegarder l'URL en BDD
    user.avatar_url = avatar_url
    db.commit()
    db.refresh(user)
    
    return user


async def delete_user_avatar(user: User, db: Session) -> dict:
    """
    Supprime la photo de profil.
    """
    if not user.avatar_url:
        return {"message": "Aucun avatar à supprimer"}
    
    # Supprimer sur Cloudinary
    await delete_avatar(user.id)
    
    # Supprimer l'URL en BDD
    user.avatar_url = None
    db.commit()
    
    return {"message": "Avatar supprimé avec succès"}
