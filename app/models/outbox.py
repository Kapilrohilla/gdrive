import datetime

from pydantic import BaseModel
from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.enum import AggregateType, OutboxStatus


class Outbox(BaseModel):
    event_name: Mapped[str] = mapped_column(String(length=255))
    aggregate_type: Mapped[AggregateType] = mapped_column(String(length=255))
    aggregate_id: Mapped[str] = mapped_column(String(length=255))
    payload: Mapped[dict] = mapped_column(JSON)
    status: OutboxStatus
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retry: Mapped[int] = mapped_column(Integer, default=3)
    next_retry_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True, default=None
    )
    published_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True, default=None
    )
    last_error: Mapped[str] = mapped_column(Text(), nullable=True, default=None)
