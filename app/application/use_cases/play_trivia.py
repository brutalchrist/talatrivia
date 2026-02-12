from typing import Optional
from uuid import uuid4, UUID
from datetime import datetime

from app.domain.entities.participation import Participation
from app.domain.entities.question import Question
from app.domain.value_objects.participation_status import ParticipationStatus
from app.application.ports.participation_repo import ParticipationRepo
from app.application.ports.question_repo import QuestionRepo
from app.application.ports.trivia_repo import TriviaRepo

class PlayTrivia:
    def __init__(
        self,
        participation_repo: ParticipationRepo,
        trivia_repo: TriviaRepo,
        question_repo: QuestionRepo,
    ):
        self.participation_repo = participation_repo
        self.trivia_repo = trivia_repo
        self.question_repo = question_repo

    async def execute(
        self, user_id: UUID, trivia_id: UUID
    ) -> tuple[Optional[Question], UUID]:
        participation = await self.participation_repo.get_by_trivia_and_user(
            trivia_id, user_id
        )

        if not participation:
            trivia = await self.trivia_repo.get_by_id(trivia_id)
            if not trivia:
                raise ValueError("Trivia not found")

            participation = Participation(
                id=uuid4(),
                trivia_id=trivia_id,
                user_id=user_id,
                status=ParticipationStatus.IN_PROGRESS,
                score_total=0,
                started_at=datetime.now(),
                finished_at=None,
            )
            participation = await self.participation_repo.save(participation)

        trivia = await self.trivia_repo.get_by_id(trivia_id)
        if not trivia or not trivia.question_ids:
            return None, participation.id
        first_question_id = trivia.question_ids[0]
        question = await self.question_repo.get_by_id(first_question_id)

        return question, participation.id
