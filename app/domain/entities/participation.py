from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from app.domain.errors import ParticipationFinished, InvalidScore
from app.domain.value_objects.participation_status import ParticipationStatus

@dataclass
class Participation:
    id: UUID
    trivia_id: UUID
    user_id: UUID
    status: ParticipationStatus
    score_total: int
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

    def can_answer(self) -> bool:
        return self.status != ParticipationStatus.FINISHED

    def add_score(self, points: int):
        if points < 0:
            raise InvalidScore("Points cannot be negative")
        self.score_total += points

    def finish(self, at: datetime):
        if self.status == ParticipationStatus.FINISHED:
            raise ParticipationFinished("Participation is already finished")
        
        self.status = ParticipationStatus.FINISHED
        self.finished_at = at
