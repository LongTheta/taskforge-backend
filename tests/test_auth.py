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


def test_register_duplicate_email(client):
    """Register with existing email fails."""
    client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "pass123"})
    resp = client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "other123"})
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"].lower()


def test_login_success(client):
    """Login with valid credentials."""
    client.post("/api/v1/auth/register", json={"email": "login@example.com", "password": "mypass"})
    resp = client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "mypass"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    """Login with wrong password fails."""
    client.post("/api/v1/auth/register", json={"email": "wrong@example.com", "password": "correct"})
    resp = client.post("/api/v1/auth/login", json={"email": "wrong@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    """Login with unregistered email fails."""
    resp = client.post("/api/v1/auth/login", json={"email": "nobody@example.com", "password": "any"})
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
