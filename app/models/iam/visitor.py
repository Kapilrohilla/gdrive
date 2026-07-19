import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String

from app.core.database import Base


class Visitor(Base):
    __tablename__ = "visitors"

    device_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSON(none_as_null=True),
        nullable=True,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    user = relationship("User", back_populates="visitors")
