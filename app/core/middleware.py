"""Request ID, structured logging, and Prometheus metrics."""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import (
    REQUEST_DURATION,
    REQUESTS_IN_PROGRESS,
    REQUESTS_TOTAL,
)

REQUEST_ID_HEADER = "X-Request-ID"

logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    """Get or generate request ID."""
    existing = request.headers.get(REQUEST_ID_HEADER)
    if existing:
        return existing
    return str(uuid.uuid4())


def _normalize_path(path: str) -> str:
    """Normalize path for metrics (avoid high cardinality from IDs)."""
    if path.startswith("/api/v1/tasks/") and path != "/api/v1/tasks":
        return "/api/v1/tasks/{id}"
    if path.startswith("/api/v1/notes/") and path != "/api/v1/notes":
        return "/api/v1/notes/{id}"
    return path


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log requests, record metrics, add X-Request-ID to response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = get_request_id(request)
        start = time.perf_counter()
        path = request.url.path
        method = request.method
        path_label = _normalize_path(path)

        REQUESTS_IN_PROGRESS.labels(method=method, path=path_label).inc()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            REQUESTS_IN_PROGRESS.labels(method=method, path=path_label).dec()
            REQUESTS_TOTAL.labels(method=method, path=path_label, status="500").inc()
            REQUEST_DURATION.labels(method=method, path=path_label).observe(
                time.perf_counter() - start
            )
            raise

        duration = time.perf_counter() - start
        duration_ms = duration * 1000

        REQUESTS_IN_PROGRESS.labels(method=method, path=path_label).dec()
        REQUESTS_TOTAL.labels(method=method, path=path_label, status=str(status_code)).inc()
        REQUEST_DURATION.labels(method=method, path=path_label).observe(duration)

        if path not in ("/health", "/ready", "/metrics") or status_code >= 400:
            logger.info(
                "%s %s %d %.1fms",
                method,
                path,
                status_code,
                duration_ms,
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )

        response.headers[REQUEST_ID_HEADER] = request_id
        return response
