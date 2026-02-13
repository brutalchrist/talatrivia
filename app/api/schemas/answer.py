from uuid import UUID
from typing import Optional
from pydantic import BaseModel

class AnswerFinishedResponse(BaseModel):
    message: str
    finished: bool
    score: int

class AnswerNextQuestionResponse(BaseModel):
    message: str
    finished: bool
    question_id: UUID
    text: str
    options: list[dict]

    class Config:
        from_attributes = True
