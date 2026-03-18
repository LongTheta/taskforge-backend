"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")


class UserLogin(BaseModel):
    """User login request."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    requires_mfa: bool = False
    mfa_challenge_token: str | None = None


class MfaSetupResponse(BaseModel):
    """MFA setup response with provisioning URI for QR code."""

    provisioning_uri: str
    secret: str  # For manual entry if QR scan fails


class MfaVerifyRequest(BaseModel):
    """MFA verification request."""

    totp_code: str = Field(..., min_length=6, max_length=6)


class MfaChallengeRequest(BaseModel):
    """MFA challenge verification during login."""

    mfa_challenge_token: str
    totp_code: str = Field(..., min_length=6, max_length=6)


class RefreshRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str
