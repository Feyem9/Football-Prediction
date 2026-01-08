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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Retourne les settings avec cache pour éviter de recharger à chaque appel."""
    return Settings()


# Instance globale des settings
settings = get_settings()
