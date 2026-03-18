"""Admin route tests."""


def test_admin_stats_requires_auth(client):
    """Admin stats without token returns 401."""
    resp = client.get("/api/v1/admin/stats")
    assert resp.status_code == 401


def test_admin_stats_forbidden_for_user(client, auth_headers):
    """Admin stats with regular user token returns 403."""
    resp = client.get("/api/v1/admin/stats", headers=auth_headers)
    assert resp.status_code == 403


def test_admin_stats_success(client, db_session):
    """Admin stats with admin user returns 200 and counts."""
    # Create admin user directly (bypass register to set role)
    from app.core.security import hash_password
    from app.models.user import User

    admin_user = User(
        email="admin@example.com",
        hashed_password=hash_password("adminpass123"),
        role="admin",
    )
    db_session.add(admin_user)
    db_session.commit()

    login_resp = client.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": "adminpass123"}
    )
    token = login_resp.json()["access_token"]
    resp = client.get("/api/v1/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "users" in data
    assert "tasks" in data
    assert "notes" in data
