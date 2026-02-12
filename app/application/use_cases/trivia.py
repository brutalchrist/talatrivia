from typing import List, Optional
from uuid import uuid4, UUID

from app.domain.entities.trivia import Trivia
from app.application.ports.trivia_repo import TriviaRepo

class CreateTrivia:
    def __init__(self, trivia_repo: TriviaRepo):
        self.trivia_repo = trivia_repo

    async def execute(
        self,
        name: str,
        question_ids: List[UUID],
        user_ids: List[UUID],
        description: Optional[str] = None,
    ) -> Trivia:
        trivia = Trivia(
            id=uuid4(),
            name=name,
            description=description,
            question_ids=question_ids,
            user_ids=user_ids,
        )
        return await self.trivia_repo.save(trivia)


class GetTrivia:
    def __init__(self, trivia_repo: TriviaRepo):
        self.trivia_repo = trivia_repo

    async def execute(self, trivia_id: UUID) -> Optional[Trivia]:
        return await self.trivia_repo.get_by_id(trivia_id)


class ListUserTrivias:
    def __init__(self, trivia_repo: TriviaRepo):
        self.trivia_repo = trivia_repo

    async def execute(self, user_id: UUID) -> List[Trivia]:
        return await self.trivia_repo.get_by_user_id(user_id)
