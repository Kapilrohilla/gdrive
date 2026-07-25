import uuid
from datetime import datetime, timezone

from app.models.iam.visitor import Visitor
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class VisitorService:
    def __init__(self):
        self.default_limit = 100

    async def get_visitor(self, db: AsyncSession):
        stmt = select(Visitor).order_by(Visitor.created_at).limit(self.default_limit)

        stmt_response = await db.execute(stmt)

        visitors = stmt_response.scalars().all()

        count_stmt = select(func.count(Visitor.id))

        count_stmt_response = await db.execute(count_stmt)

        return {"visitors": visitors, "total": count_stmt_response}

    async def get_visitor_by_id(
        self, visitor_id: uuid.UUID, db: AsyncSession
    ) -> Visitor | None:
        stmt = select(Visitor).where(Visitor.id == visitor_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def register_visitor(
        self, identifier_type: str, identifier_value: str, db: AsyncSession
    ):
        stmt = select(Visitor).where(
            Visitor.identifier_type == identifier_type,
            Visitor.identifier_value == identifier_value,
        )
        stmt_response = await db.execute(stmt)
        existing_visitor = stmt_response.scalar_one_or_none()

        if existing_visitor is None:
            new_visitor = Visitor(
                identifier_type=identifier_type, identifier_value=identifier_value
            )
            db.add(new_visitor)
            await db.commit()
            await db.refresh(new_visitor)
            return new_visitor

        return existing_visitor

    async def link_visitor_to_user(
        self, visitor_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession
    ) -> Visitor:
        visitor = await self.get_visitor_by_id(visitor_id, db)
        if visitor is None:
            raise ValueError(f"Visitor {visitor_id} not found")

        visitor.user_id = user_id
        db.add(visitor)
        await db.flush()
        return visitor

    async def touch_last_seen_at(self, visitor_id: uuid.UUID, db: AsyncSession) -> None:
        visitor = await self.get_visitor_by_id(visitor_id, db)
        if visitor is None:
            return

        visitor.last_seen_at = datetime.now(timezone.utc)
        db.add(visitor)
        await db.commit()
