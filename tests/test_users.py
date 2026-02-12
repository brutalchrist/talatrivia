from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.routes.users import get_user_repo
from app.domain.entities.user import User
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_user_repo():
    return AsyncMock()

def test_create_user(mock_user_repo):
    app.dependency_overrides[get_user_repo] = lambda: mock_user_repo
    user_data = {"name": "Test User", "email": "test@example.com"}
    expected_user = User(
        id="12345678-1234-5678-1234-567812345678",
        name="Test User",
        email="test@example.com",
    )
    mock_user_repo.save.return_value = expected_user

    response = client.post("/users", json=user_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "id" in data
    mock_user_repo.save.assert_called_once()
    
    app.dependency_overrides = {}


def test_create_user_invalid_email(mock_user_repo):
    app.dependency_overrides[get_user_repo] = lambda: mock_user_repo
    user_data = {"name": "Test User", "email": "invalid-email"}

    response = client.post("/users", json=user_data)

    assert response.status_code == 422
    
    app.dependency_overrides = {}


def test_list_users(mock_user_repo):
    app.dependency_overrides[get_user_repo] = lambda: mock_user_repo
    expected_users = [
        User(
            id="12345678-1234-5678-1234-567812345678",
            name="User 1",
            email="user1@example.com",
        ),
        User(
            id="87654321-4321-8765-4321-876543210987",
            name="User 2",
            email="user2@example.com",
        ),
    ]
    mock_user_repo.get_all.return_value = expected_users

    response = client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["email"] == "user1@example.com"
    assert data[1]["email"] == "user2@example.com"
    mock_user_repo.get_all.assert_called_once()
    
    app.dependency_overrides = {}
