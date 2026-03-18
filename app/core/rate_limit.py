"""Rate limiting configuration. Uses IP for unauthenticated requests, user_id for authenticated."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.core.config import get_settings
from app.core.security import decode_access_token


def _rate_limit_key(request: Request) -> str:
    """Use user_id from JWT when present, else IP. For login/register, no token so IP is used."""
    auth = request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            return f"user:{payload['sub']}"
    return get_remote_address(request)


def get_limiter() -> Limiter:
    """Return limiter. Set RATE_LIMIT_ENABLED=false to use very high limits (e.g. in tests)."""
    settings = get_settings()
    limit = f"{settings.rate_limit_api_per_minute}/minute" if settings.rate_limit_enabled else "10000/minute"
    return Limiter(
        key_func=_rate_limit_key,
        default_limits=[limit],
    )
