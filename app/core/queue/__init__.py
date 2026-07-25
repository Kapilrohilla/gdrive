from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enum import AggregateType, OutboxStatus
from app.models.outbox import Outbox


class EventModel(BaseModel):
    event_name: str
    aggregate_type: AggregateType
    aggregate_id: str
    payload: dict


def publish_events(db: AsyncSession, events: list[EventModel]):
    for event in events:
        publish_event(db, event)


def publish_event(db: AsyncSession, event: EventModel):
    outbox = Outbox(
        event_name=event.event_name,
        aggregate_type=event.aggregate_type,
        aggregate_id=event.aggregate_id,
        payload=event.payload,
        status=OutboxStatus.PENDING,
    )

    db.add(outbox)


def enqueue(event: Outbox):
    pass
