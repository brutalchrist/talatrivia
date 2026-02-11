from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from app.domain.errors import InvalidTriviaComposition

@dataclass
class Trivia:
    id: UUID
    name: str
    description: Optional[str]
    question_ids: List[UUID]
    user_ids: List[UUID]

    def __post_init__(self):
        if not self.name:
            raise InvalidTriviaComposition("Trivia name cannot be empty")
        
        if len(self.question_ids) != len(set(self.question_ids)):
            raise InvalidTriviaComposition("Duplicate question ids are not allowed")
            
        if len(self.user_ids) != len(set(self.user_ids)):
            raise InvalidTriviaComposition("Duplicate user ids are not allowed")
