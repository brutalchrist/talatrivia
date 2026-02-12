from typing import List, Protocol
from uuid import UUID

from app.domain.entities.user import User

class UserRepo(Protocol):
    async def save(self, user: User) -> User:
        """Saves a user to the repository."""
        ...

    async def get_all(self) -> List[User]:
        """Retrieves all users from the repository."""
        ...
