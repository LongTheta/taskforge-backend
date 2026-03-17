"""Health endpoint tests."""

import pytest


def test_health(client):
    """Health endpoint returns ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_ready(client):
    """Ready endpoint checks database."""
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"
