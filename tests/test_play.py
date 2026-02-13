from unittest.mock import AsyncMock
from uuid import UUID
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.api.routes.play import get_play_trivia_use_case
from app.domain.entities.question import Question, QuestionOption
from app.domain.value_objects.difficulty import Difficulty
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_play_trivia_use_case():
    return AsyncMock()


def test_play_trivia_first_time(mock_play_trivia_use_case):
    """Test playing trivia for the first time (creates participation)"""
    app.dependency_overrides[get_play_trivia_use_case] = (
        lambda: mock_play_trivia_use_case
    )

    user_id = UUID("33333333-3333-3333-3333-333333333333")
    trivia_id = UUID("12345678-1234-5678-1234-567812345678")
    participation_id = UUID("99999999-9999-9999-9999-999999999999")

    question = Question(
        id=UUID("11111111-1111-1111-1111-111111111111"),
        text="What is Python?",
        difficulty=Difficulty.EASY,
        options=[
            QuestionOption(
                id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
                text="A programming language",
                is_correct=True,
            ),
            QuestionOption(
                id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
                text="A snake",
                is_correct=False,
            ),
        ],
    )

    mock_play_trivia_use_case.execute.return_value = (
        question,
        participation_id,
        "Python Quiz",
        True,
        None,
    )

    response = client.get(f"/users/{user_id}/trivias/{trivia_id}/play")

    assert response.status_code == 200
    data = response.json()
    assert data["question_id"] == str(question.id)
    assert data["text"] == "What is Python?"
    assert len(data["options"]) == 2
    assert data["options"][0]["option_id"] == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    assert data["options"][0]["text"] == "A programming language"
    assert (
        data["options"][0]["answer"]
        == f"http://testserver/users/{user_id}/trivias/{trivia_id}/questions/{question.id}/options/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    )
    assert "difficulty" not in data
    assert "is_correct" not in data["options"][0]
    assert "answer" not in data
    assert data["message"] == "Comencemos con la trivia: Python Quiz. Aquí va tu primera pregunta"

    mock_play_trivia_use_case.execute.assert_called_once_with(user_id, trivia_id)

    app.dependency_overrides = {}


def test_play_trivia_in_progress(mock_play_trivia_use_case):
    """Test playing trivia when participation already exists"""
    app.dependency_overrides[get_play_trivia_use_case] = (
        lambda: mock_play_trivia_use_case
    )

    user_id = UUID("33333333-3333-3333-3333-333333333333")
    trivia_id = UUID("12345678-1234-5678-1234-567812345678")
    participation_id = UUID("99999999-9999-9999-9999-999999999999")

    question = Question(
        id=UUID("22222222-2222-2222-2222-222222222222"),
        text="What is FastAPI?",
        difficulty=Difficulty.MEDIUM,
        options=[
            QuestionOption(
                id=UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
                text="A web framework",
                is_correct=True,
            ),
            QuestionOption(
                id=UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"),
                text="A database",
                is_correct=False,
            ),
        ],
    )

    mock_play_trivia_use_case.execute.return_value = (
        question,
        participation_id,
        "JavaScript Quiz",
        False,
        None,
    )

    response = client.get(f"/users/{user_id}/trivias/{trivia_id}/play")

    assert response.status_code == 200
    data = response.json()
    assert data["question_id"] == str(question.id)
    assert data["text"] == "What is FastAPI?"
    assert data["message"] == "Continuemos con la trivia"

    app.dependency_overrides = {}


def test_play_trivia_not_found(mock_play_trivia_use_case):
    """Test playing a non-existent trivia"""
    app.dependency_overrides[get_play_trivia_use_case] = (
        lambda: mock_play_trivia_use_case
    )

    user_id = UUID("33333333-3333-3333-3333-333333333333")
    trivia_id = UUID("99999999-9999-9999-9999-999999999999")

    mock_play_trivia_use_case.execute.side_effect = ValueError("Trivia not found")

    response = client.get(f"/users/{user_id}/trivias/{trivia_id}/play")

    assert response.status_code == 404

    app.dependency_overrides = {}


def test_play_trivia_no_questions(mock_play_trivia_use_case):
    """Test playing a trivia with no questions"""
    app.dependency_overrides[get_play_trivia_use_case] = (
        lambda: mock_play_trivia_use_case
    )

    user_id = UUID("33333333-3333-3333-3333-333333333333")
    trivia_id = UUID("12345678-1234-5678-1234-567812345678")
    participation_id = UUID("99999999-9999-9999-9999-999999999999")

    mock_play_trivia_use_case.execute.return_value = (
        None,
        participation_id,
        "Empty Quiz",
        False,
        None,
    )

    response = client.get(f"/users/{user_id}/trivias/{trivia_id}/play")

    assert response.status_code == 404
    assert response.json()["detail"] == "No questions available"

    app.dependency_overrides = {}
