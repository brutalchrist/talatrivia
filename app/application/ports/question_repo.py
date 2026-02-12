from typing import List, Protocol, Optional
from uuid import UUID

from app.domain.entities.question import Question


class QuestionRepo(Protocol):
    async def save(self, question: Question) -> Question:
        """Saves a question to the repository."""
        ...

    async def get_all(self) -> List[Question]:
        """Retrieves all questions from the repository."""
        ...

    async def get_by_id(self, question_id: UUID) -> Optional[Question]:
        """Retrieves a question by ID."""
        ...
