"""Authentication tests."""

import pytest


def test_register_success(client):
    """Register a new user."""
    resp = client.post("/api/v1/auth/register", json={"email": "user@example.com", "password": "securepass123"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "user@example.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_password_too_short(client):
    """Register with password < 8 chars fails validation."""
    resp = client.post("/api/v1/auth/register", json={"email": "short@example.com", "password": "short"})
    assert resp.status_code == 422


def test_register_duplicate_email(client):
    """Register with existing email fails."""
    client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "pass12345"})
    resp = client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "other12345"})
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"].lower()


def test_login_success(client):
    """Login with valid credentials."""
    client.post("/api/v1/auth/register", json={"email": "login@example.com", "password": "mypass123"})
    resp = client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "mypass123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    """Login with wrong password fails."""
    client.post("/api/v1/auth/register", json={"email": "wrong@example.com", "password": "correct123"})
    resp = client.post("/api/v1/auth/login", json={"email": "wrong@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    """Login with unregistered email fails."""
    resp = client.post("/api/v1/auth/login", json={"email": "nobody@example.com", "password": "anypass12"})
    assert resp.status_code == 401


def test_protected_route_without_token(client):
    """Access protected route without token fails."""
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401


def test_protected_route_with_invalid_token(client):
    """Access protected route with invalid token fails."""
    resp = client.get("/api/v1/users/me", headers={"Authorization": "Bearer invalid-token"})
    assert resp.status_code == 401


def test_protected_route_with_valid_token(client, auth_headers):
    """Access protected route with valid token succeeds."""
    resp = client.get("/api/v1/users/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"
