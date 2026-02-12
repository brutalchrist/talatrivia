from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.domain.entities.user import User as DomainUser
from app.infrastructure.db.models import User as DBUser


class UserRepoSqlAlchemy:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user: DomainUser) -> DomainUser:
        db_user = DBUser(id=user.id, name=user.name, email=user.email)
        self.session.add(db_user)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise
        await self.session.refresh(db_user)
        return self._to_domain(db_user)

    async def get_all(self) -> List[DomainUser]:
        result = await self.session.execute(select(DBUser))
        db_users = result.scalars().all()
        return [self._to_domain(db_user) for db_user in db_users]

    @staticmethod
    def _to_domain(db_user: DBUser) -> DomainUser:
        return DomainUser(id=db_user.id, name=db_user.name, email=db_user.email)
