"""Notification webhook for N8N integration. Fire-and-forget POST to trigger email/SMS workflows."""

import json
import logging
import threading
from datetime import UTC, datetime
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.core.config import get_settings

ALLOWED_WEBHOOK_SCHEMES = ("https", "http")

logger = logging.getLogger(__name__)

# Actions that trigger notifications (N8N can filter further)
NOTIFY_ACTIONS = frozenset({"login_failure", "mfa_enabled", "user_registered"})


def notify_webhook(
    action: str,
    success: bool = True,
    user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | int | None = None,
    request_id: str | None = None,
    email: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    """POST audit event to N8N webhook (fire-and-forget). Use for email/SMS workflows."""
    if action not in NOTIFY_ACTIONS:
        return
    url = get_settings().notification_webhook_url
    if not url:
        return

    payload: dict[str, Any] = {
        "event_type": "audit",
        "action": action,
        "success": success,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    if user_id is not None:
        payload["user_id"] = user_id
    if resource_type is not None:
        payload["resource_type"] = resource_type
    if resource_id is not None:
        payload["resource_id"] = str(resource_id)
    if request_id is not None:
        payload["request_id"] = request_id
    if email:
        payload["email"] = email
    if extra:
        payload.update(extra)

    def _send() -> None:
        try:
            if urlparse(url).scheme not in ALLOWED_WEBHOOK_SCHEMES:
                logger.warning("Notification webhook URL scheme not allowed: %s", url)
                return
            req = Request(
                url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urlopen(req, timeout=10)  # nosec B310 -- scheme validated above
        except (URLError, HTTPError, OSError) as e:
            logger.warning("Notification webhook failed: %s", e)

    threading.Thread(target=_send, daemon=True).start()
