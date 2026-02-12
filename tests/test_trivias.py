from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.api.routes.trivias import get_trivia_repo
from app.domain.entities.trivia import Trivia
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_trivia_repo():
    return AsyncMock()


def test_create_trivia(mock_trivia_repo):
    app.dependency_overrides[get_trivia_repo] = lambda: mock_trivia_repo
    trivia_data = {
        "name": "Python Quiz",
        "description": "Test your Python knowledge",
        "question_ids": [
            "11111111-1111-1111-1111-111111111111",
            "22222222-2222-2222-2222-222222222222",
        ],
        "user_ids": ["33333333-3333-3333-3333-333333333333"],
    }
    expected_trivia = Trivia(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        name="Python Quiz",
        description="Test your Python knowledge",
        question_ids=[
            UUID("11111111-1111-1111-1111-111111111111"),
            UUID("22222222-2222-2222-2222-222222222222"),
        ],
        user_ids=[UUID("33333333-3333-3333-3333-333333333333")],
    )
    mock_trivia_repo.save.return_value = expected_trivia

    response = client.post("/trivias", json=trivia_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Python Quiz"
    assert data["description"] == "Test your Python knowledge"
    assert len(data["question_ids"]) == 2
    assert len(data["user_ids"]) == 1
    assert "id" in data
    mock_trivia_repo.save.assert_called_once()

    app.dependency_overrides = {}


def test_create_trivia_duplicate_questions(mock_trivia_repo):
    app.dependency_overrides[get_trivia_repo] = lambda: mock_trivia_repo
    trivia_data = {
        "name": "Invalid Trivia",
        "description": "Has duplicate questions",
        "question_ids": [
            "11111111-1111-1111-1111-111111111111",
            "11111111-1111-1111-1111-111111111111",
        ],
        "user_ids": ["33333333-3333-3333-3333-333333333333"],
    }

    response = client.post("/trivias", json=trivia_data)

    assert response.status_code == 422

    app.dependency_overrides = {}


def test_get_trivia(mock_trivia_repo):
    app.dependency_overrides[get_trivia_repo] = lambda: mock_trivia_repo
    trivia_id = UUID("12345678-1234-5678-1234-567812345678")
    expected_trivia = Trivia(
        id=trivia_id,
        name="Python Quiz",
        description="Test your Python knowledge",
        question_ids=[
            UUID("11111111-1111-1111-1111-111111111111"),
            UUID("22222222-2222-2222-2222-222222222222"),
        ],
        user_ids=[UUID("33333333-3333-3333-3333-333333333333")],
    )
    mock_trivia_repo.get_by_id.return_value = expected_trivia

    response = client.get(f"/trivias/{trivia_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(trivia_id)
    assert data["name"] == "Python Quiz"
    mock_trivia_repo.get_by_id.assert_called_once_with(trivia_id)

    app.dependency_overrides = {}


def test_get_trivia_not_found(mock_trivia_repo):
    app.dependency_overrides[get_trivia_repo] = lambda: mock_trivia_repo
    trivia_id = UUID("99999999-9999-9999-9999-999999999999")
    mock_trivia_repo.get_by_id.return_value = None

    response = client.get(f"/trivias/{trivia_id}")

    assert response.status_code == 404

    app.dependency_overrides = {}


def test_list_user_trivias(mock_trivia_repo):
    app.dependency_overrides[get_trivia_repo] = lambda: mock_trivia_repo
    user_id = UUID("33333333-3333-3333-3333-333333333333")
    expected_trivias = [
        Trivia(
            id=UUID("12345678-1234-5678-1234-567812345678"),
            name="Python Quiz",
            description="Test your Python knowledge",
            question_ids=[UUID("11111111-1111-1111-1111-111111111111")],
            user_ids=[user_id],
        ),
        Trivia(
            id=UUID("87654321-4321-8765-4321-876543210987"),
            name="JavaScript Quiz",
            description=None,
            question_ids=[UUID("22222222-2222-2222-2222-222222222222")],
            user_ids=[user_id],
        ),
    ]
    mock_trivia_repo.get_by_user_id.return_value = expected_trivias

    response = client.get(f"/users/{user_id}/trivias")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Python Quiz"
    assert data[1]["name"] == "JavaScript Quiz"
    mock_trivia_repo.get_by_user_id.assert_called_once_with(user_id)

    app.dependency_overrides = {}


def test_list_trivias(mock_trivia_repo):
    app.dependency_overrides[get_trivia_repo] = lambda: mock_trivia_repo
    expected_trivias = [
        Trivia(
            id=UUID("12345678-1234-5678-1234-567812345678"),
            name="Python Quiz",
            description="Test your Python knowledge",
            question_ids=[UUID("11111111-1111-1111-1111-111111111111")],
            user_ids=[UUID("33333333-3333-3333-3333-333333333333")],
        ),
        Trivia(
            id=UUID("87654321-4321-8765-4321-876543210987"),
            name="JavaScript Quiz",
            description=None,
            question_ids=[UUID("22222222-2222-2222-2222-222222222222")],
            user_ids=[UUID("44444444-4444-4444-4444-444444444444")],
        ),
    ]
    mock_trivia_repo.get_all.return_value = expected_trivias

    response = client.get("/trivias")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Python Quiz"
    assert data[1]["name"] == "JavaScript Quiz"
    mock_trivia_repo.get_all.assert_called_once()

    app.dependency_overrides = {}
