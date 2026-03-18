"""Authentication service."""

import pyotp
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decrypt_mfa_secret,
    encrypt_mfa_secret,
    generate_totp_secret,
    hash_password,
    verify_password,
    verify_totp,
)
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister


def register_user(db: Session, data: UserRegister) -> User:
    """Create a new user. Raises ValueError if email already exists."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise ValueError("Email already registered")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: UserLogin) -> User | None:
    """Authenticate user by email and password. Returns User or None."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return None
    if not verify_password(data.password, user.hashed_password):
        return None
    return user


def create_token_for_user(user: User) -> tuple[str, str]:
    """Create JWT access and refresh tokens for user. Returns (access_token, refresh_token)."""
    access = create_access_token(subject=user.id)
    refresh = create_refresh_token(subject=user.id)
    return access, refresh


def setup_mfa(db: Session, user: User) -> tuple[str, str]:
    """Generate TOTP secret for user, store encrypted, return (provisioning_uri, secret).
    Does not enable MFA until verify_mfa is called."""
    if user.role != "admin":
        raise ValueError("MFA is only available for admin users")
    secret = generate_totp_secret()
    totp = pyotp.TOTP(secret)
    issuer = "TaskForge"
    provisioning_uri = totp.provisioning_uri(name=user.email, issuer_name=issuer)
    user.mfa_secret = encrypt_mfa_secret(secret)
    user.mfa_enabled = False  # Not enabled until verified
    db.commit()
    return provisioning_uri, secret


def verify_and_enable_mfa(db: Session, user: User, totp_code: str) -> bool:
    """Verify TOTP code and enable MFA for user. Returns True on success."""
    if not user.mfa_secret:
        raise ValueError("MFA not set up. Call /auth/mfa/setup first.")
    secret = decrypt_mfa_secret(user.mfa_secret)
    if not verify_totp(secret, totp_code):
        return False
    user.mfa_enabled = True
    db.commit()
    return True


def needs_mfa_challenge(user: User) -> bool:
    """Return True if login should require MFA verification."""
    return bool(user.mfa_enabled)
