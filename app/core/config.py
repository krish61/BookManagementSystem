"""Application configuration management using Pydantic settings."""
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool = False
    ENVIRONMENT: str

    # Server Configuration
    HOST: str
    PORT: int

    # Database Configuration
    DATABASE_URL: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, database_url: str) -> str:
        """Ensure database URL uses asyncpg driver."""
        if database_url and database_url.startswith("postgresql://") and "+asyncpg" not in database_url:
            return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return database_url

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Groq API Configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str

    # Redis Configuration
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    CACHE_TTL: int

    # CORS Settings
    ALLOWED_ORIGINS: str

    # Pagination
    DEFAULT_PAGE_SIZE: int
    MAX_PAGE_SIZE: int

    def get_allowed_origins(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# Global settings instance
settings = Settings()
