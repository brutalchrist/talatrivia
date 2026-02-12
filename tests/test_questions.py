from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.routes.questions import get_question_repo
from app.domain.entities.question import Question, QuestionOption
from app.domain.value_objects.difficulty import Difficulty
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_question_repo():
    return AsyncMock()

def test_create_question(mock_question_repo):
    app.dependency_overrides[get_question_repo] = lambda: mock_question_repo
    question_data = {
        "text": "What is 2+2?",
        "difficulty": "easy",
        "options": [
            {"text": "3", "is_correct": False},
            {"text": "4", "is_correct": True},
        ],
    }
    expected_question = Question(
        id="12345678-1234-5678-1234-567812345678",
        text="What is 2+2?",
        difficulty=Difficulty.EASY,
        options=[
            QuestionOption(
                id="11111111-1111-1111-1111-111111111111",
                text="3",
                is_correct=False,
            ),
            QuestionOption(
                id="22222222-2222-2222-2222-222222222222",
                text="4",
                is_correct=True,
            ),
        ],
    )
    mock_question_repo.save.return_value = expected_question

    response = client.post("/questions", json=question_data)

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "What is 2+2?"
    assert data["difficulty"] == "easy"
    assert len(data["options"]) == 2
    assert "id" in data
    mock_question_repo.save.assert_called_once()

    app.dependency_overrides = {}


def test_create_question_invalid_options(mock_question_repo):
    app.dependency_overrides[get_question_repo] = lambda: mock_question_repo
    question_data = {
        "text": "Invalid question",
        "difficulty": "easy",
        "options": [{"text": "Only one option", "is_correct": True}],
    }

    response = client.post("/questions", json=question_data)

    assert response.status_code == 422

    app.dependency_overrides = {}


def test_list_questions(mock_question_repo):
    app.dependency_overrides[get_question_repo] = lambda: mock_question_repo
    expected_questions = [
        Question(
            id="12345678-1234-5678-1234-567812345678",
            text="Question 1",
            difficulty=Difficulty.EASY,
            options=[
                QuestionOption(
                    id="11111111-1111-1111-1111-111111111111",
                    text="Option 1",
                    is_correct=True,
                ),
                QuestionOption(
                    id="22222222-2222-2222-2222-222222222222",
                    text="Option 2",
                    is_correct=False,
                ),
            ],
        ),
        Question(
            id="87654321-4321-8765-4321-876543210987",
            text="Question 2",
            difficulty=Difficulty.MEDIUM,
            options=[
                QuestionOption(
                    id="33333333-3333-3333-3333-333333333333",
                    text="Option A",
                    is_correct=False,
                ),
                QuestionOption(
                    id="44444444-4444-4444-4444-444444444444",
                    text="Option B",
                    is_correct=True,
                ),
            ],
        ),
    ]
    mock_question_repo.get_all.return_value = expected_questions

    response = client.get("/questions")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["text"] == "Question 1"
    assert data[1]["text"] == "Question 2"
    mock_question_repo.get_all.assert_called_once()

    app.dependency_overrides = {}
