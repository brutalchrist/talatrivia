from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.api.schemas.trivia import TriviaCreate, TriviaResponse, RankingResponse
from app.application.use_cases.trivia import (
    CreateTrivia,
    GetTrivia,
    ListUserTrivias,
    ListTrivias,
    GetTriviaRanking,
)
from app.domain.errors import InvalidTriviaComposition
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.trivia_repo import TriviaRepoSqlAlchemy
from app.infrastructure.repositories.participation_repo import (
    ParticipationRepoSqlAlchemy,
)

router = APIRouter()

async def get_trivia_repo(db: AsyncSession = Depends(get_db)):
    return TriviaRepoSqlAlchemy(db)


async def get_participation_repo(db: AsyncSession = Depends(get_db)):
    return ParticipationRepoSqlAlchemy(db)

@router.post("/trivias", response_model=TriviaResponse)
async def create_trivia(
    trivia_in: TriviaCreate,
    trivia_repo: TriviaRepoSqlAlchemy = Depends(get_trivia_repo),
):
    use_case = CreateTrivia(trivia_repo)
    try:
        return await use_case.execute(
            name=trivia_in.name,
            description=trivia_in.description,
            question_ids=trivia_in.question_ids,
            user_ids=trivia_in.user_ids,
        )
    except InvalidTriviaComposition as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/trivias/{trivia_id}", response_model=TriviaResponse)
async def get_trivia(
    trivia_id: UUID, trivia_repo: TriviaRepoSqlAlchemy = Depends(get_trivia_repo)
):
    use_case = GetTrivia(trivia_repo)
    trivia = await use_case.execute(trivia_id)
    if not trivia:
        raise HTTPException(status_code=404, detail="Trivia not found")
    return trivia


@router.get("/users/{user_id}/trivias", response_model=List[TriviaResponse])
async def list_user_trivias(
    user_id: UUID, trivia_repo: TriviaRepoSqlAlchemy = Depends(get_trivia_repo)
):
    use_case = ListUserTrivias(trivia_repo)
    return await use_case.execute(user_id)


@router.get("/trivias", response_model=List[TriviaResponse])
async def list_trivias(trivia_repo: TriviaRepoSqlAlchemy = Depends(get_trivia_repo)):
    use_case = ListTrivias(trivia_repo)
    return await use_case.execute()


@router.get("/trivias/{trivia_id}/ranking", response_model=RankingResponse)
async def get_trivia_ranking(
    trivia_id: UUID,
    participation_repo: ParticipationRepoSqlAlchemy = Depends(get_participation_repo),
):
    use_case = GetTriviaRanking(participation_repo)
    ranking = await use_case.execute(trivia_id)
    return RankingResponse(trivia_id=trivia_id, ranking=ranking)
