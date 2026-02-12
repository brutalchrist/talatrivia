from typing import Protocol, Optional, List
from uuid import UUID

from app.domain.entities.answer import Answer


class AnswerRepo(Protocol):
    async def save(self, answer: Answer) -> Answer:
        """Saves an answer to the repository."""
        ...

    async def get_by_participation(self, participation_id: UUID) -> List[Answer]:
        """Retrieves all answers for a participation."""
        ...

    async def get_by_participation_and_question(
        self, participation_id: UUID, question_id: UUID
    ) -> Optional[Answer]:
        """Retrieves an answer for a specific question in a participation."""
        ...
