import uuid

from app.models import User, UserStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    def __init__(self):
        pass

    async def get_user_by_id(self, user_id: uuid.UUID, db: AsyncSession):
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        db: AsyncSession,
        full_name: str | None = None,
        avatar: str | None = None,
        status: UserStatus = UserStatus.ACTIVE,
        role_id: uuid.UUID | None = None,
    ):
        user = User(
            full_name=full_name,
            avatar=avatar,
            status=status,
            role_id=role_id,
        )
        db.add(user)
        return user
