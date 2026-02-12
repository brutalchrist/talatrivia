from uuid import UUID

from pydantic import BaseModel

from app.domain.value_objects.difficulty import Difficulty


class QuestionOptionCreate(BaseModel):
    text: str
    is_correct: bool


class QuestionCreate(BaseModel):
    text: str
    difficulty: Difficulty
    options: list[QuestionOptionCreate]


class QuestionOptionResponse(BaseModel):
    id: UUID
    text: str
    is_correct: bool

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: UUID
    text: str
    difficulty: Difficulty
    options: list[QuestionOptionResponse]

    class Config:
        from_attributes = True
