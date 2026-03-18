"""Runtime configuration. All settings from env; .env for local overrides. Production: APP_ENV=production, DATABASE_URL, SECRET_KEY."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_VERSION = "0.1.0"

INSECURE_SECRET_KEYS = frozenset(
    {
        "change-me-in-production",
        "your-secret-key-change-in-production",
        "dev-secret-key-change-in-production",
    }
)


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
    refresh_token_expire_days: int = 7
    rate_limit_login_per_minute: int = 5
    rate_limit_api_per_minute: int = 100
    rate_limit_enabled: bool = True
    mfa_required_for_admin: bool = False  # Future: when True, admin login requires TOTP
    notification_webhook_url: str | None = None  # N8N/webhook URL for email/SMS notifications
    debug: bool = False
    log_level: str = "INFO"
    git_sha: str | None = None
    image_tag: str | None = None
    app_version: str | None = None  # Override APP_VERSION; CI injects from build

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_secure_secret(self) -> bool:
        return self.secret_key not in INSECURE_SECRET_KEYS

    def validate_production(self) -> None:
        """Raise if production mode has insecure configuration."""
        if not self.is_production:
            return
        if not self.is_secure_secret:
            msg = "Production requires a secure SECRET_KEY. Generate with: openssl rand -hex 32"
            raise ValueError(msg)


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
