import asyncio

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enum import OutboxStatus
from app.core.queue import enqueue
from app.models.outbox import Outbox
from backend.app.api.deps import get_db


async def initialize_pooler(db: AsyncSession = Depends(get_db)):
    while True:
        events = await fetch_pending_events(db)

        if not events:
            await asyncio.sleep(0.5)
            continue

        for event in events:
            enqueue(event)


async def fetch_pending_events(db: AsyncSession, limit: int = 100):
    stmt = (
        select(Outbox)
        .select_from(Outbox)
        .where(
            Outbox.status == OutboxStatus.PENDING,
        )
        .order_by(Outbox.created_at)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
