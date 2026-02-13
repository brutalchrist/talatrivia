from unittest.mock import AsyncMock
from uuid import UUID
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.api.routes.play import get_answer_question_use_case
from app.domain.entities.question import Question, QuestionOption
from app.domain.value_objects.difficulty import Difficulty
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_answer_question_use_case():
    return AsyncMock()


def test_answer_question_with_next_question(mock_answer_question_use_case):
    """Test answering a question when there are more questions"""
    app.dependency_overrides[get_answer_question_use_case] = (
        lambda: mock_answer_question_use_case
    )

    user_id = UUID("33333333-3333-3333-3333-333333333333")
    trivia_id = UUID("12345678-1234-5678-1234-567812345678")
    question_id = UUID("11111111-1111-1111-1111-111111111111")
    option_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

    next_question = Question(
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

    mock_answer_question_use_case.execute.return_value = (
        next_question,
        None,
        False,
        True,
    )

    response = client.post(
        f"/users/{user_id}/trivias/{trivia_id}/questions/{question_id}/options/{option_id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["finished"] is False
    assert data["question_id"] == str(next_question.id)
    assert data["text"] == "What is FastAPI?"
    assert len(data["options"]) == 2
    assert data["options"][0]["option_id"] == str(next_question.options[0].id)
    assert (
        data["options"][0]["answer"]
        == f"http://testserver/users/{user_id}/trivias/{trivia_id}/questions/{next_question.id}/options/{next_question.options[0].id}"
    )
    assert "answer" not in data
    assert data["message"] == "¡Correcto! Vamos con la siguiente."
    mock_answer_question_use_case.execute.assert_called_once_with(
        user_id, trivia_id, question_id, option_id
    )

    app.dependency_overrides = {}


def test_answer_last_question(mock_answer_question_use_case):
    """Test answering the last question (trivia finished)"""
    app.dependency_overrides[get_answer_question_use_case] = (
        lambda: mock_answer_question_use_case
    )

    user_id = UUID("33333333-3333-3333-3333-333333333333")
    trivia_id = UUID("12345678-1234-5678-1234-567812345678")
    question_id = UUID("11111111-1111-1111-1111-111111111111")
    option_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

    final_score = 5

    mock_answer_question_use_case.execute.return_value = (None, final_score, True, True)

    response = client.post(
        f"/users/{user_id}/trivias/{trivia_id}/questions/{question_id}/options/{option_id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["finished"] is True
    assert data["score"] == final_score
    assert "question_id" not in data
    assert data["message"] == f"Trivia finalizada. Tu puntaje final es {final_score}."

    app.dependency_overrides = {}


def test_answer_question_already_answered(mock_answer_question_use_case):
    """Test answering a question that was already answered"""
    app.dependency_overrides[get_answer_question_use_case] = (
        lambda: mock_answer_question_use_case
    )

    user_id = UUID("33333333-3333-3333-3333-333333333333")
    trivia_id = UUID("12345678-1234-5678-1234-567812345678")
    question_id = UUID("11111111-1111-1111-1111-111111111111")
    option_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

    mock_answer_question_use_case.execute.side_effect = ValueError(
        "Question already answered"
    )

    response = client.post(
        f"/users/{user_id}/trivias/{trivia_id}/questions/{question_id}/options/{option_id}"
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Esa pregunta ya fue respondida. Responde la siguiente."
    )

    app.dependency_overrides = {}


def test_answer_question_participation_not_found(mock_answer_question_use_case):
    """Test answering when participation doesn't exist"""
    app.dependency_overrides[get_answer_question_use_case] = (
        lambda: mock_answer_question_use_case
    )

    user_id = UUID("33333333-3333-3333-3333-333333333333")
    trivia_id = UUID("12345678-1234-5678-1234-567812345678")
    question_id = UUID("11111111-1111-1111-1111-111111111111")
    option_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

    mock_answer_question_use_case.execute.side_effect = ValueError(
        "Participation not found"
    )

    response = client.post(
        f"/users/{user_id}/trivias/{trivia_id}/questions/{question_id}/options/{option_id}"
    )

    assert response.status_code == 400

    app.dependency_overrides = {}


def test_answer_question_invalid_option(mock_answer_question_use_case):
    """Test answering with an invalid option"""
    app.dependency_overrides[get_answer_question_use_case] = (
        lambda: mock_answer_question_use_case
    )

    user_id = UUID("33333333-3333-3333-3333-333333333333")
    trivia_id = UUID("12345678-1234-5678-1234-567812345678")
    question_id = UUID("11111111-1111-1111-1111-111111111111")
    option_id = UUID("99999999-9999-9999-9999-999999999999")

    mock_answer_question_use_case.execute.side_effect = ValueError("Option not found")

    response = client.post(
        f"/users/{user_id}/trivias/{trivia_id}/questions/{question_id}/options/{option_id}"
    )

    assert response.status_code == 400

    app.dependency_overrides = {}
