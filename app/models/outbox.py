import datetime

from sqlalchemy import JSON, DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.dialects.postgresql.named_types import EnumGenerator
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.enum import AggregateType, OutboxStatus, OutboxTopics
from app.core.database.database import Base


class Outbox(Base):
    __tablename__ = "outbox_events"

    topic: Mapped[OutboxTopics] = mapped_column(EnumGenerator(OutboxTopics, name="outbox_topics"))
    aggregate_type: Mapped[AggregateType] = mapped_column(
        SQLEnum(AggregateType, name="aggregate_type"),
        nullable=False,
    )
    aggregate_id: Mapped[str] = mapped_column(String(length=255))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[OutboxStatus] = mapped_column(
        SQLEnum(OutboxStatus, name="outbox_status"),
        nullable=False,
        default=OutboxStatus.PENDING,
    )
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retry: Mapped[int] = mapped_column(Integer, default=3)
    next_retry_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )
    published_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )
    last_error: Mapped[str | None] = mapped_column(Text(), nullable=True, default=None)
