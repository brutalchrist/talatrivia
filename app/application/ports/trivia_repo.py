from typing import List, Protocol, Optional
from uuid import UUID

from app.domain.entities.trivia import Trivia

class TriviaRepo(Protocol):
    async def save(self, trivia: Trivia) -> Trivia:
        """Saves a trivia to the repository."""
        ...

    async def get_by_id(self, trivia_id: UUID) -> Optional[Trivia]:
        """Retrieves a trivia by ID."""
        ...

    async def get_by_user_id(self, user_id: UUID) -> List[Trivia]:
        """Retrieves all trivias assigned to a user."""
        ...
