"""Config and production validation tests."""

import pytest

from app.core.config import Settings


def test_validate_production_raises_on_insecure_secret():
    """Production with insecure SECRET_KEY raises ValueError."""
    settings = Settings(
        app_env="production",
        secret_key="change-me-in-production",
        database_url="postgresql://localhost/test",
    )
    with pytest.raises(ValueError, match="secure SECRET_KEY"):
        settings.validate_production()


def test_validate_production_passes_with_secure_secret():
    """Production with secure SECRET_KEY does not raise."""
    settings = Settings(
        app_env="production",
        secret_key="a" * 32,
        database_url="postgresql://localhost/test",
    )
    settings.validate_production()


def test_validate_production_skips_non_production():
    """Development and test skip validation."""
    for env in ("development", "test"):
        settings = Settings(
            app_env=env,
            secret_key="change-me-in-production",
            database_url="postgresql://localhost/test",
        )
        settings.validate_production()
