from unittest.mock import AsyncMock
from uuid import UUID, uuid4
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.routes.trivias import get_participation_repo
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_participation_repo():
    return AsyncMock()


def test_get_trivia_ranking(mock_participation_repo):
    app.dependency_overrides[get_participation_repo] = lambda: mock_participation_repo
    trivia_id = uuid4()
    
    expected_ranking = [
        {
            "user_id": uuid4(),
            "user_name": "User 1",
            "score": 100,
            "finished_at": datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        },
        {
            "user_id": uuid4(),
            "user_name": "User 2",
            "score": 90,
            "finished_at": datetime(2023, 1, 1, 10, 5, 0, tzinfo=timezone.utc),
        },
    ]
    mock_participation_repo.get_ranking.return_value = expected_ranking

    response = client.get(f"/trivias/{trivia_id}/ranking")

    assert response.status_code == 200
    data = response.json()
    assert data["trivia_id"] == str(trivia_id)
    assert len(data["ranking"]) == 2
    assert data["ranking"][0]["user_name"] == "User 1"
    assert data["ranking"][0]["score"] == 100
    assert data["ranking"][1]["user_name"] == "User 2"
    assert data["ranking"][1]["score"] == 90
    
    mock_participation_repo.get_ranking.assert_called_once_with(trivia_id)

    app.dependency_overrides = {}


def test_get_trivia_ranking_empty(mock_participation_repo):
    app.dependency_overrides[get_participation_repo] = lambda: mock_participation_repo
    trivia_id = uuid4()
    
    mock_participation_repo.get_ranking.return_value = []

    response = client.get(f"/trivias/{trivia_id}/ranking")

    assert response.status_code == 200
    data = response.json()
    assert data["trivia_id"] == str(trivia_id)
    assert len(data["ranking"]) == 0
    
    mock_participation_repo.get_ranking.assert_called_once_with(trivia_id)

    app.dependency_overrides = {}
