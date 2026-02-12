from typing import List
from uuid import uuid4

from app.domain.entities.question import Question, QuestionOption
from app.application.ports.question_repo import QuestionRepo


class CreateQuestion:
    def __init__(self, question_repo: QuestionRepo):
        self.question_repo = question_repo

    async def execute(
        self, text: str, difficulty: str, options: List[dict]
    ) -> Question:
        question_options = [
            QuestionOption(
                id=uuid4(), text=opt["text"], is_correct=opt["is_correct"]
            )
            for opt in options
        ]
        question = Question(
            id=uuid4(), text=text, difficulty=difficulty, options=question_options
        )
        return await self.question_repo.save(question)


class ListQuestions:
    def __init__(self, question_repo: QuestionRepo):
        self.question_repo = question_repo

    async def execute(self) -> List[Question]:
        return await self.question_repo.get_all()
