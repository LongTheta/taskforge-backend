"""User schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr


class UserResponse(UserBase):
    """User response schema."""

    id: int
    is_active: bool
    role: str = "user"
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
