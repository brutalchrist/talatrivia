from typing import List
from uuid import uuid4

from app.domain.entities.user import User
from app.application.ports.user_repo import UserRepo

class CreateUser:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def execute(self, name: str, email: str) -> User:
        user = User(id=uuid4(), name=name, email=email)
        return await self.user_repo.save(user)


class ListUsers:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def execute(self) -> List[User]:
        return await self.user_repo.get_all()
