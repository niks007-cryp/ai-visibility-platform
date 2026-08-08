from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "AI Visibility Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # PostgreSQL configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres_secret_password"
    POSTGRES_DB: str = "ai_visibility_db"
    
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres_secret_password@localhost:5432/ai_visibility_db"
    )

    # JWT Secret — inject via SECRET_KEY environment variable in production
    SECRET_KEY: str = "production_super_secret_jwt_signing_key_change_in_env"

    # Redis broker URL
    REDIS_URL: Optional[str] = None

    # Gemini AI Provider configuration
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # CORS configuration
    CORS_ORIGINS: List[str] = ["*"]

    @property
    def async_database_url(self) -> str:
        """Returns database URL formatted for SQLAlchemy asyncpg."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
