"""Authentication schemas."""

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
