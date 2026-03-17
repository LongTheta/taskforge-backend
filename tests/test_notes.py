"""Note CRUD tests."""

import pytest


def test_create_note(client, auth_headers):
    """Create a note."""
    resp = client.post(
        "/api/v1/notes",
        headers=auth_headers,
        json={"title": "My note", "content": "Some content here", "tags": ["work"]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My note"
    assert data["content"] == "Some content here"
    assert data["tags"] == ["work"]
    assert "id" in data


def test_list_notes(client, auth_headers):
    """List user's notes."""
    client.post("/api/v1/notes", headers=auth_headers, json={"title": "Note 1", "content": "C1"})
    client.post("/api/v1/notes", headers=auth_headers, json={"title": "Note 2", "content": "C2"})
    resp = client.get("/api/v1/notes", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_note(client, auth_headers):
    """Get note by ID."""
    create = client.post("/api/v1/notes", headers=auth_headers, json={"title": "Get me", "content": "Body"})
    note_id = create.json()["id"]
    resp = client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Get me"


def test_get_note_not_found(client, auth_headers):
    """Get nonexistent note returns 404."""
    resp = client.get("/api/v1/notes/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_update_note(client, auth_headers):
    """Update a note."""
    create = client.post("/api/v1/notes", headers=auth_headers, json={"title": "Original", "content": "Old"})
    note_id = create.json()["id"]
    resp = client.patch(
        f"/api/v1/notes/{note_id}",
        headers=auth_headers,
        json={"title": "Updated", "content": "New content"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"
    assert resp.json()["content"] == "New content"


def test_delete_note(client, auth_headers):
    """Delete a note."""
    create = client.post("/api/v1/notes", headers=auth_headers, json={"title": "To delete", "content": "X"})
    note_id = create.json()["id"]
    resp = client.delete(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert resp.status_code == 204
    get_resp = client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_note_user_scoping(client, auth_headers):
    """User A cannot access User B's note."""
    client.post("/api/v1/auth/register", json={"email": "b@example.com", "password": "pass"})
    login_b = client.post("/api/v1/auth/login", json={"email": "b@example.com", "password": "pass"})
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}
    create = client.post("/api/v1/notes", headers=headers_b, json={"title": "B's note", "content": "Secret"})
    note_id = create.json()["id"]

    resp = client.get(f"/api/v1/notes/{note_id}", headers=auth_headers)
    assert resp.status_code == 404
