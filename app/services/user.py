import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserStatus
from app.models.iam.user import User


class UserService:
    async def get_user(self, db: AsyncSession):
        query = select(User)
        query_response = await db.execute(query)
        return query_response.scalars().all()

    async def create_user(
        self,
        db: AsyncSession,
        full_name: str | None = None,
        avatar: str | None = None,
        role_id: uuid.UUID | None = None,
    ):
        user = User(
            full_name=full_name,
            avatar=avatar,
            status=UserStatus.ACTIVE,
            role_id=role_id,
        )
        db.add(user)
        return user

    async def get_user_by_id(self, user_id: uuid.UUID, db: AsyncSession):
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()


user_service = UserService()
