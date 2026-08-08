import uuid

from sqlalchemy import Enum as SQLEnum, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.enum import (
    ResourceEventActions,
    ResourceEventActorType,
    ResourceEventResourceType,
)
from app.core.database.database import Base


class ResourceEvents(Base):
    __tablename__ = "resource_events"

    action: Mapped[ResourceEventActions] = mapped_column(
        SQLEnum(ResourceEventActions, name="resource_event_action"),
        nullable=False,
    )

    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    actor_type: Mapped[ResourceEventActorType] = mapped_column(
        SQLEnum(ResourceEventActorType, name="resource_event_actor_type"),
        nullable=False,
    )

    resource_id: Mapped[str] = mapped_column(String(length=255), nullable=False)
    resource_type: Mapped[ResourceEventResourceType] = mapped_column(
        SQLEnum(ResourceEventResourceType, name="resource_event_resource_type"),
        nullable=False,
    )

    event_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(length=255), nullable=True)


__all__ = ["ResourceEvents"]
