"""Authentication routes."""

from fastapi import APIRouter, HTTPException, Request, status
from slowapi.util import get_remote_address

from app.api.deps import DbSession, require_role
from app.core.audit import audit_log
from app.core.notify import notify_webhook
from app.core.config import get_settings
from app.core.middleware import get_request_id
from app.core.rate_limit import get_limiter
from app.core.security import (
    create_mfa_challenge_token,
    decode_mfa_challenge_token,
    decrypt_mfa_secret,
    verify_totp,
)
from app.models.user import User
from app.schemas.auth import (
    MfaChallengeRequest,
    MfaSetupResponse,
    MfaVerifyRequest,
    RefreshRequest,
    Token,
    UserLogin,
    UserRegister,
)
from app.schemas.user import UserResponse
from app.services.auth_service import (
    authenticate_user,
    create_token_for_user,
    needs_mfa_challenge,
    register_user,
    setup_mfa,
    verify_and_enable_mfa,
)

limiter = get_limiter()

router = APIRouter(prefix="/auth", tags=["auth"])


def _login_limit() -> str:
    s = get_settings()
    if not s.rate_limit_enabled:
        return "10000/minute"
    return f"{s.rate_limit_login_per_minute}/minute"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(_login_limit, key_func=get_remote_address)
def register(request: Request, data: UserRegister, db: DbSession):
    """Register a new user."""
    request_id = get_request_id(request)
    try:
        user = register_user(db, data)
        audit_log(
            action="user_registered",
            user_id=user.id,
            resource_type="user",
            resource_id=user.id,
            success=True,
            request_id=request_id,
        )
        notify_webhook(
            action="user_registered",
            success=True,
            user_id=user.id,
            resource_type="user",
            resource_id=user.id,
            request_id=request_id,
            email=user.email,
        )
        return user
    except ValueError as e:
        audit_log(
            action="user_registration_failed",
            success=False,
            request_id=request_id,
            extra={"reason": str(e)},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=Token)
@limiter.limit(_login_limit, key_func=get_remote_address)
def login(request: Request, data: UserLogin, db: DbSession):
    """Authenticate and return JWT access token. If MFA enabled, returns requires_mfa + challenge token."""
    request_id = get_request_id(request)
    user = authenticate_user(db, data)
    if not user:
        audit_log(
            action="login_failure",
            success=False,
            request_id=request_id,
            extra={"reason": "invalid_credentials"},
        )
        notify_webhook(
            action="login_failure",
            success=False,
            request_id=request_id,
            email=data.email,
            extra={"reason": "invalid_credentials"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if needs_mfa_challenge(user):
        audit_log(
            action="mfa_challenge_issued",
            user_id=user.id,
            success=True,
            request_id=request_id,
        )
        challenge_token = create_mfa_challenge_token(user.id)
        return Token(
            access_token="",
            refresh_token=None,
            requires_mfa=True,
            mfa_challenge_token=challenge_token,
        )
    audit_log(
        action="login_success",
        user_id=user.id,
        success=True,
        request_id=request_id,
    )
    access_token, refresh_token = create_token_for_user(user)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/verify-mfa", response_model=Token)
@limiter.limit(_login_limit, key_func=get_remote_address)
def verify_mfa(request: Request, data: MfaChallengeRequest, db: DbSession):
    """Complete login by verifying TOTP code. Call after login returns requires_mfa."""
    request_id = get_request_id(request)
    payload = decode_mfa_challenge_token(data.mfa_challenge_token)
    if not payload or "sub" not in payload:
        audit_log(
            action="mfa_verify_failure",
            success=False,
            request_id=request_id,
            extra={"reason": "invalid_challenge_token"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA challenge",
        )
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active or not user.mfa_secret:
        audit_log(
            action="mfa_verify_failure",
            success=False,
            request_id=request_id,
            extra={"reason": "user_not_found_or_mfa_not_setup"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA challenge",
        )
    secret = decrypt_mfa_secret(user.mfa_secret)
    if not verify_totp(secret, data.totp_code):
        audit_log(
            action="mfa_verify_failure",
            user_id=user.id,
            success=False,
            request_id=request_id,
            extra={"reason": "invalid_totp"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )
    audit_log(
        action="login_success",
        user_id=user.id,
        success=True,
        request_id=request_id,
        extra={"mfa_verified": True},
    )
    access_token, refresh_token = create_token_for_user(user)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/mfa/setup", response_model=MfaSetupResponse)
@limiter.limit(_login_limit, key_func=get_remote_address)
def mfa_setup(
    request: Request,
    db: DbSession,
    current_user: User = require_role("admin"),
):
    """Generate MFA secret and return provisioning URI. Admin only. Call mfa/verify to enable."""
    request_id = get_request_id(request)
    try:
        provisioning_uri, secret = setup_mfa(db, current_user)
    except ValueError as e:
        audit_log(
            action="mfa_setup_failure",
            user_id=current_user.id,
            success=False,
            request_id=request_id,
            extra={"reason": str(e)},
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    audit_log(
        action="mfa_setup",
        user_id=current_user.id,
        success=True,
        request_id=request_id,
    )
    return MfaSetupResponse(provisioning_uri=provisioning_uri, secret=secret)


@router.post("/mfa/verify")
@limiter.limit(_login_limit, key_func=get_remote_address)
def mfa_verify(
    request: Request,
    data: MfaVerifyRequest,
    db: DbSession,
    current_user: User = require_role("admin"),
):
    """Verify TOTP code and enable MFA. Admin only. Call after mfa/setup."""
    request_id = get_request_id(request)
    try:
        ok = verify_and_enable_mfa(db, current_user, data.totp_code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not ok:
        audit_log(
            action="mfa_verify_failure",
            user_id=current_user.id,
            success=False,
            request_id=request_id,
            extra={"reason": "invalid_totp"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
        )
    audit_log(
        action="mfa_enabled",
        user_id=current_user.id,
        success=True,
        request_id=request_id,
    )
    notify_webhook(
        action="mfa_enabled",
        success=True,
        user_id=current_user.id,
        request_id=request_id,
        email=current_user.email,
    )
    return {"detail": "MFA enabled successfully"}


@router.post("/refresh", response_model=Token)
@limiter.limit(_login_limit, key_func=get_remote_address)
def refresh(request: Request, data: RefreshRequest, db: DbSession):
    """Exchange a valid refresh token for new access and refresh tokens."""
    from app.core.security import decode_refresh_token
    from app.models.user import User

    request_id = get_request_id(request)
    payload = decode_refresh_token(data.refresh_token)
    if not payload or "sub" not in payload:
        audit_log(
            action="refresh_failure",
            success=False,
            request_id=request_id,
            extra={"reason": "invalid_refresh_token"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        audit_log(
            action="refresh_failure",
            success=False,
            request_id=request_id,
            extra={"reason": "user_not_found_or_inactive"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    audit_log(
        action="token_refreshed",
        user_id=user.id,
        success=True,
        request_id=request_id,
    )
    access_token, refresh_token = create_token_for_user(user)
    return Token(access_token=access_token, refresh_token=refresh_token)
