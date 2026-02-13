from uuid import UUID
from typing import Optional
from datetime import datetime

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


class RankingEntry(BaseModel):
    user_id: UUID
    user_name: str
    score: int
    finished_at: Optional[datetime] = None


class RankingResponse(BaseModel):
    trivia_id: UUID
    ranking: list[RankingEntry]
