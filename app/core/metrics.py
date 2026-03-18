"""Prometheus metrics for request count, duration, in-flight."""

from prometheus_client import Counter, Gauge, Histogram, generate_latest

from app.core.config import APP_VERSION, get_settings

REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests in progress",
    ["method", "path"],
)

# Build info for Grafana/dashboard correlation (env, version, git_sha)
BUILD_INFO = Gauge(
    "taskforge_build_info",
    "Build metadata (version, env). Value 1.",
    ["version", "env", "git_sha"],
)


def _ensure_build_info_registered() -> None:
    """Register build_info metric once with current deployment metadata."""
    settings = get_settings()
    version = settings.app_version or APP_VERSION
    git_sha = settings.git_sha or "unknown"
    try:
        BUILD_INFO.labels(version=version, env=settings.app_env, git_sha=git_sha).set(1)
    except ValueError:
        pass  # Already registered


def get_metrics() -> bytes:
    """Return Prometheus exposition format (text/plain)."""
    _ensure_build_info_registered()
    return generate_latest()
