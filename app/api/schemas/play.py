from uuid import UUID
from pydantic import BaseModel

class PlayQuestionOption(BaseModel):
    option_id: UUID
    text: str
    answer: str

class PlayQuestionResponse(BaseModel):
    question_id: UUID
    text: str
    options: list[PlayQuestionOption]

    class Config:
        from_attributes = True
