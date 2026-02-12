from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.domain.entities.trivia import Trivia as DomainTrivia
from app.infrastructure.db.models import (
    Trivia as DBTrivia,
    TriviaQuestion,
    TriviaUser,
)

class TriviaRepoSqlAlchemy:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, trivia: DomainTrivia) -> DomainTrivia:
        db_trivia = DBTrivia(
            id=trivia.id, name=trivia.name, description=trivia.description
        )
        self.session.add(db_trivia)

        # Add question associations
        for question_id in trivia.question_ids:
            trivia_question = TriviaQuestion(
                trivia_id=trivia.id, question_id=question_id
            )
            self.session.add(trivia_question)

        # Add user associations
        for user_id in trivia.user_ids:
            trivia_user = TriviaUser(trivia_id=trivia.id, user_id=user_id)
            self.session.add(trivia_user)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

        await self.session.refresh(db_trivia)
        return self._to_domain(db_trivia)

    async def get_by_id(self, trivia_id: UUID) -> Optional[DomainTrivia]:
        result = await self.session.execute(
            select(DBTrivia)
            .options(selectinload(DBTrivia.questions), selectinload(DBTrivia.users))
            .where(DBTrivia.id == trivia_id)
        )
        db_trivia = result.scalar_one_or_none()
        return self._to_domain(db_trivia) if db_trivia else None

    async def get_by_user_id(self, user_id: UUID) -> List[DomainTrivia]:
        result = await self.session.execute(
            select(DBTrivia)
            .join(TriviaUser, DBTrivia.id == TriviaUser.trivia_id)
            .options(selectinload(DBTrivia.questions), selectinload(DBTrivia.users))
            .where(TriviaUser.user_id == user_id)
        )
        db_trivias = result.scalars().all()
        return [self._to_domain(db_trivia) for db_trivia in db_trivias]

    async def get_all(self) -> List[DomainTrivia]:
        result = await self.session.execute(
            select(DBTrivia).options(
                selectinload(DBTrivia.questions), selectinload(DBTrivia.users)
            )
        )
        db_trivias = result.scalars().all()
        return [self._to_domain(db_trivia) for db_trivia in db_trivias]

    @staticmethod
    def _to_domain(db_trivia: DBTrivia) -> DomainTrivia:
        return DomainTrivia(
            id=db_trivia.id,
            name=db_trivia.name,
            description=db_trivia.description,
            question_ids=[q.id for q in db_trivia.questions],
            user_ids=[u.id for u in db_trivia.users],
        )
