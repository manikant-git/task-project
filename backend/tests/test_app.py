"""
backend/tests/test_app.py
Unit + Integration tests for the TaskFlow Flask API.
GitHub Actions runs these automatically on every push.
"""

import pytest
import json
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, init_db


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture(scope="session")
def setup_db():
    """Initialize DB once for all tests."""
    init_db()

@pytest.fixture
def client(setup_db):
    """Create a test client for each test."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ──────────────────────────────────────────────
# HEALTH CHECK TESTS
# ──────────────────────────────────────────────

def test_health_check(client):
    """API should return healthy status."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "ok"
    assert "service" in data


# ──────────────────────────────────────────────
# GET TASKS TESTS
# ──────────────────────────────────────────────

def test_get_tasks_returns_list(client):
    """GET /api/tasks should return a list."""
    res = client.get("/api/tasks")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert isinstance(data, list)


# ──────────────────────────────────────────────
# CREATE TASK TESTS
# ──────────────────────────────────────────────

def test_create_task_success(client):
    """POST /api/tasks should create a task."""
    payload = {
        "title": "Test Task from CI",
        "priority": "high",
        "description": "Created by automated test"
    }
    res = client.post(
        "/api/tasks",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert res.status_code == 201
    data = json.loads(res.data)
    assert data["title"] == "Test Task from CI"
    assert data["priority"] == "high"
    assert data["status"] == "pending"
    assert "id" in data


def test_create_task_missing_title(client):
    """POST without title should return 400."""
    res = client.post(
        "/api/tasks",
        data=json.dumps({"priority": "low"}),
        content_type="application/json"
    )
    assert res.status_code == 400
    data = json.loads(res.data)
    assert "error" in data


def test_create_task_invalid_priority(client):
    """POST with invalid priority should return 400."""
    res = client.post(
        "/api/tasks",
        data=json.dumps({"title": "Bad Task", "priority": "urgent"}),
        content_type="application/json"
    )
    assert res.status_code == 400


def test_create_task_default_priority(client):
    """POST without priority should default to medium."""
    res = client.post(
        "/api/tasks",
        data=json.dumps({"title": "Default Priority Task"}),
        content_type="application/json"
    )
    assert res.status_code == 201
    data = json.loads(res.data)
    assert data["priority"] == "medium"


# ──────────────────────────────────────────────
# UPDATE TASK TESTS
# ──────────────────────────────────────────────

def test_update_task_status(client):
    """PUT /api/tasks/<id> should update status to done."""
    # First create a task
    res = client.post(
        "/api/tasks",
        data=json.dumps({"title": "Task to Complete"}),
        content_type="application/json"
    )
    task_id = json.loads(res.data)["id"]

    # Mark as done
    res = client.put(
        f"/api/tasks/{task_id}",
        data=json.dumps({"status": "done"}),
        content_type="application/json"
    )
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["status"] == "done"


def test_update_task_invalid_status(client):
    """PUT with invalid status should return 400."""
    res = client.post(
        "/api/tasks",
        data=json.dumps({"title": "Another Task"}),
        content_type="application/json"
    )
    task_id = json.loads(res.data)["id"]

    res = client.put(
        f"/api/tasks/{task_id}",
        data=json.dumps({"status": "cancelled"}),
        content_type="application/json"
    )
    assert res.status_code == 400


def test_update_nonexistent_task(client):
    """PUT on missing task should return 404."""
    res = client.put(
        "/api/tasks/999999",
        data=json.dumps({"status": "done"}),
        content_type="application/json"
    )
    assert res.status_code == 404


# ──────────────────────────────────────────────
# DELETE TASK TESTS
# ──────────────────────────────────────────────

def test_delete_task(client):
    """DELETE /api/tasks/<id> should remove the task."""
    # Create
    res = client.post(
        "/api/tasks",
        data=json.dumps({"title": "Task to Delete"}),
        content_type="application/json"
    )
    task_id = json.loads(res.data)["id"]

    # Delete
    res = client.delete(f"/api/tasks/{task_id}")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["id"] == task_id

    # Confirm gone — update should 404
    res = client.put(
        f"/api/tasks/{task_id}",
        data=json.dumps({"status": "done"}),
        content_type="application/json"
    )
    assert res.status_code == 404


def test_delete_nonexistent_task(client):
    """DELETE on missing task should return 404."""
    res = client.delete("/api/tasks/999999")
    assert res.status_code == 404
