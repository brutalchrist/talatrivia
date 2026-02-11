from dataclasses import dataclass
from typing import List
from uuid import UUID

from app.domain.errors import InvalidQuestionOptions
from app.domain.value_objects.difficulty import Difficulty

@dataclass(frozen=True)
class QuestionOption:
    id: UUID
    text: str
    is_correct: bool

@dataclass
class Question:
    id: UUID
    text: str
    difficulty: Difficulty
    options: List[QuestionOption]

    def __post_init__(self):
        self._validate_options()

    def _validate_options(self):
        if len(self.options) < 2:
            raise InvalidQuestionOptions("Question must have at least 2 options")
        
        correct_count = sum(1 for option in self.options if option.is_correct)
        if correct_count != 1:
            raise InvalidQuestionOptions("Question must have exactly 1 correct option")

    def correct_option_id(self) -> UUID:
        for option in self.options:
            if option.is_correct:
                return option.id
        raise InvalidQuestionOptions("No correct option found")

    def is_option_valid(self, option_id: UUID) -> bool:
        return any(option.id == option_id for option in self.options)
