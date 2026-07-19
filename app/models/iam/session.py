import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Session(Base):
    __tablename__ = "sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    identity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identities.id"),
        nullable=False,
    )

    refresh_token_hash: Mapped[str] = mapped_column(Text(), nullable=False)

    device_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    browser: Mapped[str | None] = mapped_column(String(200), nullable=True)

    os: Mapped[str | None] = mapped_column(String(200), nullable=True)

    ip: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship("User", back_populates="sessions")
    identity = relationship("Identity", back_populates="sessions")
    auth_events = relationship("AuthEvent", back_populates="session")
