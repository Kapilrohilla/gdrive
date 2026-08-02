import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.iam.user import User
from app.services.iam.identity import IdentityService


class UserProfile:
    def __init__(
        self,
        id: uuid.UUID,
        full_name: str | None,
        email: str,
        avatar: str | None,
        status,
    ):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.avatar = avatar
        self.status = status


class UserService:
    def __init__(self):
        self.identity_service = IdentityService()

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
        from app.models import UserStatus

        user = User(
            full_name=full_name,
            avatar=avatar,
            status=UserStatus.ACTIVE,
            role_id=role_id,
        )
        db.add(user)
        return user

    async def get_user_by_id(self, user_id: uuid.UUID, db: AsyncSession) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_profile(
        self, db: AsyncSession, user_id: uuid.UUID, identity_id: uuid.UUID
    ) -> UserProfile:
        user = await self.get_user_by_id(user_id, db)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        identity = await self.identity_service.get_identity_by_id(identity_id, db)
        email = identity.identifier if identity is not None else ""

        return UserProfile(
            id=user.id,
            full_name=user.full_name,
            email=email,
            avatar=user.avatar,
            status=user.status,
        )


user_service = UserService()
