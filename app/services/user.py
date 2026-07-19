from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.iam.user import User


class UserService:
    async def get_user(self, db: AsyncSession):
        query = select(User)
        query_response = await db.execute(query)
        return query_response.scalars().all()

    async def create_user(self, full_name: str, db: AsyncSession):
        user = User(full_name=full_name)
        db.add(user)
        await db.commit()
        return {user.id}


user_service = UserService()
