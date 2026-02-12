from typing import List, Protocol

from app.domain.entities.question import Question


class QuestionRepo(Protocol):
    async def save(self, question: Question) -> Question:
        """Saves a question to the repository."""
        ...

    async def get_all(self) -> List[Question]:
        """Retrieves all questions from the repository."""
        ...
