from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class Answer:
    id: UUID
    participation_id: UUID
    trivia_id: UUID
    question_id: UUID
    option_id: UUID
    is_correct: bool
    score_awarded: int
    answered_at: Optional[datetime]
