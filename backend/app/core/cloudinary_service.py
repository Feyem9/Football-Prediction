import cloudinary
import cloudinary.uploader
from fastapi import UploadFile, HTTPException, status
from core.config import settings

# Configuration Cloudinary
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)


async def upload_avatar(file: UploadFile, user_id: int) -> str:
    """
    Upload une image avatar sur Cloudinary.
    
    Args:
        file: Fichier image uploadé
        user_id: ID de l'utilisateur (pour nommer le fichier)
        
    Returns:
        URL sécurisée de l'image uploadée
        
    Raises:
        HTTPException: Si le fichier n'est pas une image valide
    """
    # Vérifier le type de fichier
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de fichier non supporté. Formats acceptés: JPEG, PNG, GIF, WebP"
        )
    
    # Vérifier la taille (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fichier trop volumineux. Maximum 5MB"
        )
    
    try:
        # Upload sur Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder="pronoscore/avatars",
            public_id=f"user_{user_id}",
            overwrite=True,
            resource_type="image",
            transformation=[
                {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
                {"quality": "auto", "fetch_format": "auto"}
            ]
        )
        
        return result["secure_url"]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur upload Cloudinary: {str(e)}"
        )


async def delete_avatar(user_id: int) -> bool:
    """
    Supprime l'avatar d'un utilisateur sur Cloudinary.
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        True si supprimé, False sinon
    """
    try:
        public_id = f"pronoscore/avatars/user_{user_id}"
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception:
        return False
