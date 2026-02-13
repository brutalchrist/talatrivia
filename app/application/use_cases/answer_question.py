from typing import Optional
from uuid import uuid4, UUID
from datetime import datetime

from app.domain.entities.answer import Answer
from app.domain.entities.question import Question
from app.domain.entities.participation import Participation
from app.domain.services.scoring import score_for
from app.domain.value_objects.participation_status import ParticipationStatus
from app.application.ports.answer_repo import AnswerRepo
from app.application.ports.participation_repo import ParticipationRepo
from app.application.ports.question_repo import QuestionRepo
from app.application.ports.trivia_repo import TriviaRepo

class AnswerQuestion:
    def __init__(
        self,
        answer_repo: AnswerRepo,
        participation_repo: ParticipationRepo,
        question_repo: QuestionRepo,
        trivia_repo: TriviaRepo,
    ):
        self.answer_repo = answer_repo
        self.participation_repo = participation_repo
        self.question_repo = question_repo
        self.trivia_repo = trivia_repo

    async def execute(
        self,
        user_id: UUID,
        trivia_id: UUID,
        question_id: UUID,
        option_id: UUID,
    ) -> tuple[Optional[Question], Optional[int], bool, bool]:
        participation = await self.participation_repo.get_by_trivia_and_user(
            trivia_id, user_id
        )
        if not participation:
            raise ValueError("Participation not found")

        if not participation.can_answer():
            raise ValueError("Participation is already finished")

        existing_answer = await self.answer_repo.get_by_participation_and_question(
            participation.id, question_id
        )
        if existing_answer:
            raise ValueError("Question already answered")

        question = await self.question_repo.get_by_id(question_id)
        if not question:
            raise ValueError("Question not found")

        selected_option = next(
            (opt for opt in question.options if opt.id == option_id), None
        )
        if not selected_option:
            raise ValueError("Option not found")

        is_correct = selected_option.is_correct
        score_awarded = score_for(question.difficulty) if is_correct else 0

        answer = Answer(
            id=uuid4(),
            participation_id=participation.id,
            trivia_id=trivia_id,
            question_id=question_id,
            option_id=option_id,
            is_correct=is_correct,
            score_awarded=score_awarded,
            answered_at=datetime.now(),
        )
        await self.answer_repo.save(answer)

        participation.add_score(score_awarded)

        trivia = await self.trivia_repo.get_by_id(trivia_id)
        if not trivia:
            raise ValueError("Trivia not found")

        answered_questions = await self.answer_repo.get_by_participation(
            participation.id
        )
        answered_question_ids = {ans.question_id for ans in answered_questions}

        next_question_id = next(
            (qid for qid in trivia.question_ids if qid not in answered_question_ids),
            None,
        )

        if next_question_id:
            await self.participation_repo.update(participation)
            next_question = await self.question_repo.get_by_id(next_question_id)
            return next_question, None, False, is_correct
        else:
            participation.finish(datetime.now())
            await self.participation_repo.update(participation)
            return None, participation.score_total, True, is_correct
