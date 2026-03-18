# MFA Design

## Current State

- JWT access + refresh tokens
- RBAC (user, admin roles)
- **MFA (TOTP)** — admin users can enable TOTP; login requires verification when enabled

## Recommendation

**Admin users should use MFA.** For regulated or high-privilege environments, add TOTP (e.g. Google Authenticator) for admin role.

## Extension Point

The auth flow can be extended without major refactor:

1. **User model:** Add `mfa_secret` (encrypted) and `mfa_enabled` columns when implementing.
2. **Login flow:** After password success, if `user.mfa_enabled` and `user.role == "admin"`:
   - Return `requires_mfa: true` and `mfa_challenge_token` (short-lived, single-use)
   - Client calls new endpoint `POST /auth/verify-mfa` with TOTP code
   - On success, issue access + refresh tokens
3. **Endpoints (implemented):**
   - `POST /api/v1/auth/mfa/setup` — generate secret, return provisioning URI (admin only)
   - `POST /api/v1/auth/mfa/verify` — verify TOTP, enable MFA (admin only)
   - `POST /api/v1/auth/verify-mfa` — verify during login (when challenge issued)

## Library Options

- `pyotp` — TOTP generation and verification
- `qrcode` — QR code for TOTP setup

## Scope

- **Phase 1:** Design documented
- **Phase 2 (implemented):** TOTP for admin role; user role remains password-only
- **Phase 3 (optional):** Allow optional MFA for all users
