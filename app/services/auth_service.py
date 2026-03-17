"""Authentication service."""

from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
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


def create_token_for_user(user: User) -> str:
    """Create JWT access token for user."""
    return create_access_token(subject=user.id)
