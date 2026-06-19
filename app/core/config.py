from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from app.core.logger import logger
from typing import Optional


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
  
    PROJECT_NAME: str = "FastAPI Application"
    DEBUG: str = "release"
    SECRET_KEY: str
    WHATSAPP_API_KEY: Optional[str] = None

    # Google OAuth Settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    # LinkedIn OAuth Settings
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_REDIRECT_URI: Optional[str] = None

    # Frontend base URL — used to redirect back after OAuth callback
    FRONTEND_URL: str = "http://127.0.0.1:5500"

    # Database Settings
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # Computed Property for MySQL URL
    @property
    def DATABASE_URL(self) -> str:
        logger.info("Constructing the database URL from environment variables.")
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")

settings = Settings()
