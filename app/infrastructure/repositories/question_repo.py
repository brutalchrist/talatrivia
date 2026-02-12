from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.domain.entities.question import Question as DomainQuestion, QuestionOption as DomainQuestionOption
from app.infrastructure.db.models import Question as DBQuestion, QuestionOption as DBQuestionOption


class QuestionRepoSqlAlchemy:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, question: DomainQuestion) -> DomainQuestion:
        db_question = DBQuestion(
            id=question.id, text=question.text, difficulty=question.difficulty
        )
        self.session.add(db_question)

        for option in question.options:
            db_option = DBQuestionOption(
                id=option.id,
                question_id=question.id,
                text=option.text,
                is_correct=option.is_correct,
            )
            self.session.add(db_option)

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

        await self.session.refresh(db_question)
        return self._to_domain(db_question)

    async def get_all(self) -> List[DomainQuestion]:
        result = await self.session.execute(
            select(DBQuestion).options(selectinload(DBQuestion.options))
        )
        db_questions = result.scalars().all()
        return [self._to_domain(db_question) for db_question in db_questions]

    @staticmethod
    def _to_domain(db_question: DBQuestion) -> DomainQuestion:
        options = [
            DomainQuestionOption(
                id=opt.id, text=opt.text, is_correct=opt.is_correct
            )
            for opt in db_question.options
        ]
        return DomainQuestion(
            id=db_question.id,
            text=db_question.text,
            difficulty=db_question.difficulty,
            options=options,
        )
