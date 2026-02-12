from typing import Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.schemas.play import PlayQuestionResponse, PlayQuestionOption
from app.api.schemas.answer import AnswerFinishedResponse, AnswerNextQuestionResponse
from app.application.use_cases.play_trivia import PlayTrivia
from app.application.use_cases.answer_question import AnswerQuestion
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.participation_repo import (
    ParticipationRepoSqlAlchemy,
)
from app.infrastructure.repositories.trivia_repo import TriviaRepoSqlAlchemy
from app.infrastructure.repositories.question_repo import QuestionRepoSqlAlchemy
from app.infrastructure.repositories.answer_repo import AnswerRepoSqlAlchemy

router = APIRouter()

async def get_play_trivia_use_case(db: AsyncSession = Depends(get_db)):
    participation_repo = ParticipationRepoSqlAlchemy(db)
    trivia_repo = TriviaRepoSqlAlchemy(db)
    question_repo = QuestionRepoSqlAlchemy(db)
    return PlayTrivia(participation_repo, trivia_repo, question_repo)


async def get_answer_question_use_case(db: AsyncSession = Depends(get_db)):
    answer_repo = AnswerRepoSqlAlchemy(db)
    participation_repo = ParticipationRepoSqlAlchemy(db)
    question_repo = QuestionRepoSqlAlchemy(db)
    trivia_repo = TriviaRepoSqlAlchemy(db)
    return AnswerQuestion(answer_repo, participation_repo, question_repo, trivia_repo)


@router.get(
    "/users/{user_id}/trivias/{trivia_id}/play", response_model=PlayQuestionResponse
)
async def play_trivia(
    user_id: UUID,
    trivia_id: UUID,
    use_case: PlayTrivia = Depends(get_play_trivia_use_case),
):
    try:
        question, participation_id = await use_case.execute(user_id, trivia_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not question:
        raise HTTPException(status_code=404, detail="No questions available")

    options = [
        PlayQuestionOption(
            option_id=opt.id,
            text=opt.text,
            answer=f"/users/{user_id}/trivias/{trivia_id}/questions/{question.id}/options/{opt.id}",
        )
        for opt in question.options
    ]

    return PlayQuestionResponse(
        question_id=question.id, text=question.text, options=options
    )


@router.post(
    "/users/{user_id}/trivias/{trivia_id}/questions/{question_id}/options/{option_id}",
    response_model=Union[AnswerNextQuestionResponse, AnswerFinishedResponse],
)
async def answer_question(
    user_id: UUID,
    trivia_id: UUID,
    question_id: UUID,
    option_id: UUID,
    use_case: AnswerQuestion = Depends(get_answer_question_use_case),
):
    try:
        next_question, final_score, is_finished = await use_case.execute(
            user_id, trivia_id, question_id, option_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if is_finished:
        return AnswerFinishedResponse(finished=True, score=final_score)

    options = [
        {
            "option_id": str(opt.id),
            "text": opt.text,
            "answer": f"/users/{user_id}/trivias/{trivia_id}/questions/{next_question.id}/options/{opt.id}",
        }
        for opt in next_question.options
    ]

    return AnswerNextQuestionResponse(
        finished=False,
        question_id=next_question.id,
        text=next_question.text,
        options=options,
    )
