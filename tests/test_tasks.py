"""Task CRUD tests."""


def test_create_task(client, auth_headers):
    """Create a task."""
    resp = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "My task", "description": "Do something", "priority": "high"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My task"
    assert data["description"] == "Do something"
    assert data["priority"] == "high"
    assert data["status"] == "todo"
    assert "id" in data


def test_list_tasks(client, auth_headers):
    """List user's tasks."""
    client.post("/api/v1/tasks", headers=auth_headers, json={"title": "Task 1"})
    client.post("/api/v1/tasks", headers=auth_headers, json={"title": "Task 2"})
    resp = client.get("/api/v1/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_tasks_filter_by_status(client, auth_headers):
    """List tasks filtered by status."""
    client.post("/api/v1/tasks", headers=auth_headers, json={"title": "Todo 1", "status": "todo"})
    client.post("/api/v1/tasks", headers=auth_headers, json={"title": "Done 1", "status": "done"})
    resp = client.get("/api/v1/tasks?status=todo", headers=auth_headers)
    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "todo"


def test_list_tasks_empty(client, auth_headers):
    """List tasks when none exist."""
    resp = client.get("/api/v1/tasks", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_task(client, auth_headers):
    """Get task by ID."""
    create = client.post("/api/v1/tasks", headers=auth_headers, json={"title": "Get me"})
    task_id = create.json()["id"]
    resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Get me"


def test_get_task_not_found(client, auth_headers):
    """Get nonexistent task returns 404."""
    resp = client.get("/api/v1/tasks/99999", headers=auth_headers)
    assert resp.status_code == 404


def test_update_task(client, auth_headers):
    """Update a task."""
    create = client.post(
        "/api/v1/tasks", headers=auth_headers, json={"title": "Original", "status": "todo"}
    )
    task_id = create.json()["id"]
    resp = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
        json={"status": "done", "title": "Updated"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "done"
    assert resp.json()["title"] == "Updated"


def test_delete_task(client, auth_headers):
    """Delete a task."""
    create = client.post("/api/v1/tasks", headers=auth_headers, json={"title": "To delete"})
    task_id = create.json()["id"]
    resp = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 204
    get_resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_task_user_scoping(client, auth_headers):
    """User A cannot access User B's task."""
    # Create user A and task
    client.post("/api/v1/auth/register", json={"email": "a@example.com", "password": "pass12345"})
    login_a = client.post(
        "/api/v1/auth/login", json={"email": "a@example.com", "password": "pass12345"}
    )
    headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}
    create = client.post("/api/v1/tasks", headers=headers_a, json={"title": "A's task"})
    task_id = create.json()["id"]

    # User B (from auth_headers - test@example.com) tries to access
    resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 404  # Not found - user scoped
