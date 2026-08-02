from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql.named_types import EnumGenerator
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String

from app.constants.enum import VisitorAppType
from app.core.database.database import Base


class Visitor(Base):
    __tablename__ = "visitors"
    __table_args__ = (
        UniqueConstraint("identifier_type", "identifier_value", name="uix_visitor_identifier"),
    )

    identifier_type: Mapped[str] = mapped_column(String(100), nullable=False)
    identifier_value: Mapped[str] = mapped_column(String(100), nullable=False)

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    app_type: Mapped[VisitorAppType] = mapped_column(EnumGenerator(VisitorAppType), nullable=False)

    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSON(none_as_null=True),
        nullable=True,
    )

    sessions = relationship("Session", back_populates="visitor")
