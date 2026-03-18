"""Health and metrics endpoint tests."""

import pytest


def test_health(client):
    """Health endpoint returns ok with service info."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "taskforge-backend"
    assert "version" in data
    assert data["env"] == "test"


def test_ready(client):
    """Ready endpoint checks database connectivity."""
    resp = client.get("/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


def test_metrics(client):
    """Metrics endpoint returns Prometheus format."""
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers.get("content-type", "")
    assert "http_requests_total" in resp.text or "http_request_duration" in resp.text


def test_request_id_in_response(client):
    """Response includes X-Request-ID header."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert "x-request-id" in [h.lower() for h in resp.headers.keys()]
