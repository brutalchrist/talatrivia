from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.domain.entities.participation import Participation as DomainParticipation
from app.infrastructure.db.models import Participation as DBParticipation

class ParticipationRepoSqlAlchemy:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, participation: DomainParticipation) -> DomainParticipation:
        db_participation = DBParticipation(
            id=participation.id,
            trivia_id=participation.trivia_id,
            user_id=participation.user_id,
            status=participation.status,
            score_total=participation.score_total,
            started_at=participation.started_at,
            finished_at=participation.finished_at,
        )
        self.session.add(db_participation)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

        await self.session.refresh(db_participation)
        return self._to_domain(db_participation)

    async def get_by_trivia_and_user(
        self, trivia_id: UUID, user_id: UUID
    ) -> Optional[DomainParticipation]:
        result = await self.session.execute(
            select(DBParticipation).where(
                DBParticipation.trivia_id == trivia_id,
                DBParticipation.user_id == user_id,
            )
        )
        db_participation = result.scalar_one_or_none()
        return self._to_domain(db_participation) if db_participation else None

    async def update(self, participation: DomainParticipation) -> DomainParticipation:
        result = await self.session.execute(
            select(DBParticipation).where(DBParticipation.id == participation.id)
        )
        db_participation = result.scalar_one_or_none()
        if not db_participation:
            raise ValueError("Participation not found")

        db_participation.status = participation.status
        db_participation.score_total = participation.score_total
        db_participation.finished_at = participation.finished_at

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

        await self.session.refresh(db_participation)
        return self._to_domain(db_participation)

    @staticmethod
    def _to_domain(db_participation: DBParticipation) -> DomainParticipation:
        return DomainParticipation(
            id=db_participation.id,
            trivia_id=db_participation.trivia_id,
            user_id=db_participation.user_id,
            status=db_participation.status,
            score_total=db_participation.score_total,
            started_at=db_participation.started_at,
            finished_at=db_participation.finished_at,
        )
