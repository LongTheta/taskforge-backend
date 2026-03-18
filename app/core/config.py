"""Application configuration from environment variables.

All secrets must come from env vars. Never hardcode secrets.
Local dev: defaults are acceptable when DEBUG=true or DATABASE_URL points to localhost.
Production: set DATABASE_URL, SECRET_KEY explicitly.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database - REQUIRED in production. Default for local dev only.
    database_url: str = "postgresql://taskforge:taskforge@localhost:5432/taskforge"

    # Security - REQUIRED in production. Generate: openssl rand -hex 32
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # App
    debug: bool = False
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
