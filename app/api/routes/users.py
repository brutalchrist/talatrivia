from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.user import UserCreate, UserResponse
from app.application.use_cases.user import CreateUser, ListUsers
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.user_repo import UserRepoSqlAlchemy

router = APIRouter()

async def get_user_repo(db: AsyncSession = Depends(get_db)):
    return UserRepoSqlAlchemy(db)

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_in: UserCreate, user_repo: UserRepoSqlAlchemy = Depends(get_user_repo)
):
    use_case = CreateUser(user_repo)
    return await use_case.execute(name=user_in.name, email=user_in.email)


@router.get("/users", response_model=List[UserResponse])
async def list_users(user_repo: UserRepoSqlAlchemy = Depends(get_user_repo)):
    use_case = ListUsers(user_repo)
    return await use_case.execute()
