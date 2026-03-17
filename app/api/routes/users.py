"""User routes."""

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: CurrentUser):
    """Get the current authenticated user's profile."""
    return current_user
