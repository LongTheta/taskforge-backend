"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.schemas.auth import Token, UserLogin, UserRegister
from app.schemas.user import UserResponse
from app.services.auth_service import authenticate_user, create_token_for_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: DbSession):
    """Register a new user."""
    try:
        user = register_user(db, data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: DbSession):
    """Authenticate and return JWT access token."""
    user = authenticate_user(db, data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_token_for_user(user)
    return Token(access_token=token)
