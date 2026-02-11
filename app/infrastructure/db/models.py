import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    String,
    Text,
    Boolean,
    ForeignKey,
    Integer,
    DateTime,
    Enum,
    UniqueConstraint,
    Index,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base, UUIDMixin, TimestampMixin


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ParticipationStatus(str, enum.Enum):
    in_progress = "in_progress"
    finished = "finished"


class TriviaQuestion(Base, TimestampMixin):
    __tablename__ = "trivia_questions"

    trivia_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trivias.id"), primary_key=True
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id"), primary_key=True
    )

    __table_args__ = (Index("ix_trivia_questions_question_id", "question_id"),)


class TriviaUser(Base, TimestampMixin):
    __tablename__ = "trivia_users"

    trivia_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trivias.id"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )

    __table_args__ = (Index("ix_trivia_users_user_id", "user_id"),)


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    # Relationships
    participations: Mapped[List["Participation"]] = relationship(
        back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )
    trivias: Mapped[List["Trivia"]] = relationship(
        secondary="trivia_users", back_populates="users", lazy="selectin"
    )


class Question(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "questions"

    text: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(
        Enum(Difficulty, native_enum=False), nullable=False
    )

    # Relationships
    options: Mapped[List["QuestionOption"]] = relationship(
        back_populates="question", lazy="selectin", cascade="all, delete-orphan"
    )
    trivias: Mapped[List["Trivia"]] = relationship(
        secondary="trivia_questions", back_populates="questions", lazy="selectin"
    )


class QuestionOption(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "question_options"

    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    question: Mapped["Question"] = mapped_column(use_existing_column=True) # Workaround for back_populates issue if mapped_column is used for FK
    question: Mapped["Question"] = relationship(back_populates="options")
    
    __table_args__ = (Index("ix_question_options_question_id", "question_id"),)


class Trivia(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "trivias"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    participations: Mapped[List["Participation"]] = relationship(
        back_populates="trivia", lazy="selectin", cascade="all, delete-orphan"
    )
    questions: Mapped[List["Question"]] = relationship(
        secondary="trivia_questions", back_populates="trivias", lazy="selectin"
    )
    users: Mapped[List["User"]] = relationship(
        secondary="trivia_users", back_populates="trivias", lazy="selectin"
    )


class Participation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "participations"

    trivia_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trivias.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[ParticipationStatus] = mapped_column(
        Enum(ParticipationStatus, native_enum=False),
        nullable=False,
        default=ParticipationStatus.in_progress,
    )
    score_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="participations")
    trivia: Mapped["Trivia"] = relationship(back_populates="participations")
    answers: Mapped[List["Answer"]] = relationship(
        back_populates="participation", lazy="selectin", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("trivia_id", "user_id", name="uq_participation_trivia_user"),
        Index("ix_participations_trivia_id", "trivia_id"),
        Index("ix_participations_user_id", "user_id"),
    )


class Answer(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "answers"

    participation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("participations.id"), nullable=False
    )
    trivia_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trivias.id"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id"), nullable=False
    )
    option_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("question_options.id"), nullable=False
    )
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    answered_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    participation: Mapped["Participation"] = relationship(back_populates="answers")
    option: Mapped["QuestionOption"] = relationship()
    
    # We can define a relationship to question via option or directly if needed, but the schema has direct FKs.
    # To enforce the composite FK to trivia_questions, we rely on the database constraint (ForeignKeyConstraint),
    # but SQLAlchemy Declarative is cleaner with independent FKs + a table arg tuple if we want to be explicit about the composite FK,
    # or just trust the individual FKs.
    # The prompt asks for: FK compuesta (trivia_id, question_id) -> trivia_questions(trivia_id, question_id)
    
    __table_args__ = (
        UniqueConstraint("participation_id", "question_id", name="uq_answer_participation_question"),
        ForeignKeyConstraint(
            ["trivia_id", "question_id"],
            ["trivia_questions.trivia_id", "trivia_questions.question_id"],
            name="fk_answers_trivia_question",
        ),
        Index("ix_answers_participation_id", "participation_id"),
        Index("ix_answers_option_id", "option_id"),
        Index("ix_answers_trivia_question", "trivia_id", "question_id"),
    )


