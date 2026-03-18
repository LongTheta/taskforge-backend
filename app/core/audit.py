"""Audit logging for security-relevant actions. Do not log passwords or tokens."""

import logging
from typing import Any

logger = logging.getLogger("audit")


def audit_log(
    action: str,
    user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | int | None = None,
    success: bool = True,
    request_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """Log an audit event. All fields except action are optional."""
    log_data: dict[str, Any] = {
        "event_type": "audit",
        "action": action,
        "success": success,
    }
    if user_id is not None:
        log_data["user_id"] = user_id
    if resource_type is not None:
        log_data["resource_type"] = resource_type
    if resource_id is not None:
        log_data["resource_id"] = str(resource_id)
    if request_id is not None:
        log_data["request_id"] = request_id
    if extra:
        log_data.update(extra)

    logger.info(
        "audit | action=%s success=%s",
        action,
        success,
        extra=log_data,
    )
