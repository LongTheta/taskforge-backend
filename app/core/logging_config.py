"""Structured logging. JSON when DEBUG=false (prod); human-readable when DEBUG=true."""

import json
import logging
import sys

from app.core.config import APP_VERSION, get_settings


class DeploymentContextFilter(logging.Filter):
    """Inject service, version, env into log records for Loki correlation."""

    def filter(self, record: logging.LogRecord) -> bool:
        settings = get_settings()
        record.service = "taskforge-backend"
        record.version = settings.app_version or APP_VERSION
        record.env = settings.app_env
        return True


def configure_logging() -> None:
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)
    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if settings.debug:
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    else:
        formatter = JsonFormatter()

    handler.setFormatter(formatter)
    root.addHandler(handler)
    if not settings.debug:
        root.addFilter(DeploymentContextFilter())


class JsonFormatter(logging.Formatter):
    """JSON formatter for Grafana/Loki."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "service"):
            log_data["service"] = record.service
        if hasattr(record, "version"):
            log_data["version"] = record.version
        if hasattr(record, "env"):
            log_data["env"] = record.env
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        # Audit event fields
        if hasattr(record, "event_type"):
            log_data["event_type"] = record.event_type
        if hasattr(record, "action"):
            log_data["action"] = record.action
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "resource_type"):
            log_data["resource_type"] = record.resource_type
        if hasattr(record, "resource_id"):
            log_data["resource_id"] = record.resource_id
        if hasattr(record, "success"):
            log_data["success"] = record.success
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)
