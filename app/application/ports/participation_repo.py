from typing import Protocol, Optional
from uuid import UUID
from datetime import datetime

from app.domain.entities.participation import Participation


class ParticipationRepo(Protocol):
    async def save(self, participation: Participation) -> Participation:
        """Saves a participation to the repository."""
        ...

    async def get_by_trivia_and_user(
        self, trivia_id: UUID, user_id: UUID
    ) -> Optional[Participation]:
        """Retrieves a participation by trivia and user."""
        ...

    async def update(self, participation: Participation) -> Participation:
        """Updates an existing participation."""
        ...

    async def get_ranking(self, trivia_id: UUID) -> list[dict]:
        """Retrieves the ranking for a trivia."""
        ...
