from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import DbSession
from app.constants.enum import AggregateType, OutboxTopics
from app.models import Outbox


class OutboxMessage(BaseModel):
    topic: OutboxTopics
    aggregate_type: AggregateType
    aggregate_id: str
    payload: dict
    max_retry: int = 3


class OutboxService:
    async def send_message(self, db: DbSession, message: OutboxMessage) -> Outbox:
        outbox = Outbox(**message.model_dump())
        db.add(outbox)
        await db.flush()
        return outbox

    async def get_message(self, db: DbSession, message_id: str):
        stmt = select(Outbox).where(Outbox.id == message_id)
        outbox = await db.execute(stmt)
        return outbox.scalar_one_or_none()
