import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.short_urls import ShortUrls
from app.services.utils.encoding import EncodingService


class ShortUrlsService:
    def __init__(self, encoding_service: EncodingService):
        self.encoding_service = encoding_service

    async def shorten(self, db: AsyncSession, long_url: str, user_id: uuid.UUID) -> str:
        result = await db.execute(
            select(ShortUrls).where(
                ShortUrls.original_url == long_url,
                ShortUrls.user_id == user_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None and existing.short_code is not None:
            return existing.short_code

        record = ShortUrls(original_url=long_url, user_id=user_id)
        db.add(record)
        await db.flush()

        short_code = self.encoding_service.encode_base62(record.id)
        record.short_code = short_code
        await db.commit()

        return short_code

    async def get_short_urls(
        self,
        db: AsyncSession,
        user_id: uuid.UUID | None = None,
    ) -> list[ShortUrls]:
        query = select(ShortUrls).order_by(ShortUrls.created_at.desc())
        if user_id is not None:
            query = query.where(ShortUrls.user_id == user_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def resolve(self, db: AsyncSession, short_code: str) -> str | None:
        result = await db.execute(
            select(ShortUrls.original_url).where(ShortUrls.short_code == short_code)
        )
        return result.scalar_one_or_none()
