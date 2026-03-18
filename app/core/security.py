"""Security utilities: password hashing, JWT handling, and MFA."""

import base64
import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt
import pyotp
from cryptography.fernet import Fernet
from jwt import PyJWTError

from app.core.config import get_settings


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str | int, extra_claims: dict[str, Any] | None = None) -> str:
    """Create a JWT access token."""
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "access"}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str | int) -> str:
    """Create a JWT refresh token (longer-lived, type=refresh)."""
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    to_encode: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate an access JWT. Returns payload or None if invalid."""
    payload = _decode_token(token)
    if payload and payload.get("type") in ("access", None):  # None = legacy token
        return payload
    return None


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a refresh JWT. Returns payload or None if invalid."""
    payload = _decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None


def _decode_token(token: str) -> dict[str, Any] | None:
    """Decode JWT without type check."""
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except PyJWTError:
        return None


def _fernet_key() -> bytes:
    """Derive a Fernet key from SECRET_KEY."""
    key = hashlib.sha256(get_settings().secret_key.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_mfa_secret(plain: str) -> str:
    """Encrypt TOTP secret for storage."""
    f = Fernet(_fernet_key())
    return f.encrypt(plain.encode()).decode()


def decrypt_mfa_secret(encrypted: str) -> str:
    """Decrypt stored TOTP secret."""
    f = Fernet(_fernet_key())
    return f.decrypt(encrypted.encode()).decode()


def create_mfa_challenge_token(subject: str | int) -> str:
    """Create short-lived JWT for MFA verification step."""
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=5)
    to_encode: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "mfa_challenge"}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_mfa_challenge_token(token: str) -> dict[str, Any] | None:
    """Decode and validate MFA challenge JWT."""
    payload = _decode_token(token)
    if payload and payload.get("type") == "mfa_challenge":
        return payload
    return None


def generate_totp_secret() -> str:
    """Generate a new TOTP secret for MFA setup."""
    return pyotp.random_base32()


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code against the secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)
