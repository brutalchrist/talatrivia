from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.question import QuestionCreate, QuestionResponse
from app.application.use_cases.question import CreateQuestion, ListQuestions
from app.domain.errors import InvalidQuestionOptions
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.question_repo import QuestionRepoSqlAlchemy

router = APIRouter()

async def get_question_repo(db: AsyncSession = Depends(get_db)):
    return QuestionRepoSqlAlchemy(db)

@router.post("/questions", response_model=QuestionResponse)
async def create_question(
    question_in: QuestionCreate,
    question_repo: QuestionRepoSqlAlchemy = Depends(get_question_repo),
):
    use_case = CreateQuestion(question_repo)
    options_data = [opt.model_dump() for opt in question_in.options]
    try:
        return await use_case.execute(
            text=question_in.text,
            difficulty=question_in.difficulty,
            options=options_data,
        )
    except InvalidQuestionOptions as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/questions", response_model=List[QuestionResponse])
async def list_questions(
    question_repo: QuestionRepoSqlAlchemy = Depends(get_question_repo)
):
    use_case = ListQuestions(question_repo)
    return await use_case.execute()
