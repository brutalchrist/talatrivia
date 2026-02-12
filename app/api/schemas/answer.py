from uuid import UUID
from typing import Optional
from pydantic import BaseModel

class AnswerFinishedResponse(BaseModel):
    finished: bool
    score: int

class AnswerNextQuestionResponse(BaseModel):
    finished: bool
    question_id: UUID
    text: str
    options: list[dict]

    class Config:
        from_attributes = True
