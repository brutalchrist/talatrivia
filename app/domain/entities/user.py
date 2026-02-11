from dataclasses import dataclass
from uuid import UUID

from app.domain.errors import InvalidEmail

@dataclass
class User:
    id: UUID
    name: str
    email: str

    def __post_init__(self):
        if not self.email:
            raise InvalidEmail("Email cannot be empty")
