from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Settings(BaseSettings):
    """Configuration centralisée de l'application."""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    
    # JWT Configuration
    secret_key: str = os.getenv("SECRET_KEY", "")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    password_reset_expire_hours: int = int(os.getenv("PASSWORD_RESET_EXPIRE_HOURS", "1"))
    
    # SMTP Configuration
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    from_email: str = os.getenv("FROM_EMAIL", "noreply@pronoscore.com")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
    
    # App Configuration
    app_name: str = "Pronoscore"
    env: str = os.getenv("ENV", "development")  # development, production
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Cloudinary
    cloudinary_cloud_name: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    cloudinary_api_key: str = os.getenv("CLOUDINARY_API_KEY", "")
    cloudinary_api_secret: str = os.getenv("CLOUDINARY_API_SECRET", "")
    
    # Football-Data.org API
    football_data_api_key: str = os.getenv("FOOTBALL_DATA_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Retourne les settings avec cache pour éviter de recharger à chaque appel."""
    return Settings()


# Instance globale des settings
settings = get_settings()

