from uuid import UUID
from typing import Optional

from pydantic import BaseModel

class TriviaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    question_ids: list[UUID]
    user_ids: list[UUID]


class TriviaResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    question_ids: list[UUID]
    user_ids: list[UUID]

    class Config:
        from_attributes = True
