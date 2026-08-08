from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.platform.config import AppConfig


class ConfigService:
    async def list_configs(self, db: AsyncSession) -> list[AppConfig]:
        result = await db.execute(select(AppConfig).order_by(AppConfig.key))
        return list(result.scalars().all())

    async def get_config(self, db: AsyncSession, key: str) -> AppConfig:
        result = await db.execute(select(AppConfig).where(AppConfig.key == key))
        config = result.scalar_one_or_none()
        if config is None:
            raise HTTPException(status_code=404, detail="Config not found")
        return config

    async def upsert_config(self, db: AsyncSession, key: str, value: dict) -> AppConfig:
        result = await db.execute(select(AppConfig).where(AppConfig.key == key))
        config = result.scalar_one_or_none()

        if config is None:
            config = AppConfig(key=key, value=value)
            db.add(config)
        else:
            config.value = value
            db.add(config)

        await db.commit()
        await db.refresh(config)
        return config

    async def delete_config(self, db: AsyncSession, key: str) -> None:
        config = await self.get_config(db, key)
        await db.delete(config)
        await db.commit()


__all__ = ["ConfigService"]
