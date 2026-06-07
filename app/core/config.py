from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # FastAPI
    PROJECT_NAME: str = "Media Service"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str  # asyncpg URL

    # JWT (from Django)
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_TOKEN_PREFIX: str = "Bearer"

    # GCS
    GCS_BUCKET_NAME: str
    GCS_PROJECT_ID: str | None = None
    # Optional path to a Google service account JSON credentials file
    GCS_CREDENTIALS_FILE: str | None = None

    # Limits
    MAX_UPLOAD_SIZE_MB: int = 50
    DAILY_UPLOAD_LIMIT: int = 3

    # Allowed file types
    ALLOWED_EXTENSIONS: List[str] = ["mp4", "mov", "mkv", "avi", "webm", "jpg", "jpeg", "png", "gif", "pdf"]
    ALLOWED_MIME_TYPES: List[str] = [
        "video/mp4", "video/quicktime", "video/x-matroska", "video/x-msvideo",
        "video/webm", "image/jpeg", "image/png", "image/gif", "application/pdf"
    ]

settings = Settings()