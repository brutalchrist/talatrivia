from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.domain.entities.answer import Answer as DomainAnswer
from app.infrastructure.db.models import Answer as DBAnswer

class AnswerRepoSqlAlchemy:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, answer: DomainAnswer) -> DomainAnswer:
        db_answer = DBAnswer(
            id=answer.id,
            participation_id=answer.participation_id,
            trivia_id=answer.trivia_id,
            question_id=answer.question_id,
            option_id=answer.option_id,
            is_correct=answer.is_correct,
            score_awarded=answer.score_awarded,
            answered_at=answer.answered_at,
        )
        self.session.add(db_answer)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

        await self.session.refresh(db_answer)
        return self._to_domain(db_answer)

    async def get_by_participation(self, participation_id: UUID) -> List[DomainAnswer]:
        result = await self.session.execute(
            select(DBAnswer).where(DBAnswer.participation_id == participation_id)
        )
        db_answers = result.scalars().all()
        return [self._to_domain(db_answer) for db_answer in db_answers]

    async def get_by_participation_and_question(
        self, participation_id: UUID, question_id: UUID
    ) -> Optional[DomainAnswer]:
        result = await self.session.execute(
            select(DBAnswer).where(
                DBAnswer.participation_id == participation_id,
                DBAnswer.question_id == question_id,
            )
        )
        db_answer = result.scalar_one_or_none()
        return self._to_domain(db_answer) if db_answer else None

    @staticmethod
    def _to_domain(db_answer: DBAnswer) -> DomainAnswer:
        return DomainAnswer(
            id=db_answer.id,
            participation_id=db_answer.participation_id,
            trivia_id=db_answer.trivia_id,
            question_id=db_answer.question_id,
            option_id=db_answer.option_id,
            is_correct=db_answer.is_correct,
            score_awarded=db_answer.score_awarded,
            answered_at=db_answer.answered_at,
        )
