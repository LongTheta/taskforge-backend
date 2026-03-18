"""Runtime configuration. Secrets from env only. Production: APP_ENV=production, DATABASE_URL, SECRET_KEY."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_VERSION = "0.1.0"

INSECURE_SECRET_KEYS = frozenset({
    "change-me-in-production",
    "your-secret-key-change-in-production",
    "dev-secret-key-change-in-production",
})


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_env: Literal["development", "production", "test"] = "development"
    database_url: str = "postgresql://taskforge:taskforge@localhost:5432/taskforge"
    secret_key: str = "change-me-in-production"  # Production: openssl rand -hex 32
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    debug: bool = False
    log_level: str = "INFO"
    git_sha: str | None = None

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_secure_secret(self) -> bool:
        return self.secret_key not in INSECURE_SECRET_KEYS


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
