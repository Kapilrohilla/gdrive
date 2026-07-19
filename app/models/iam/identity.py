import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class IdentityProvider(str, Enum):
    PASSWORD = "password"
    MAGIC_LINK = "magic_link"
    OTP = "otp"


class IdentityStatus(str, Enum):
    PENDING = "verification_pending"
    ACTIVE = "active"
    BLOCKED = "blocked"


class Identity(Base):
    __tablename__ = "identities"

    provider: Mapped[IdentityProvider] = mapped_column(
        SQLEnum(IdentityProvider, name="identity_provider"),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )

    identifier: Mapped[str] = mapped_column(String(500), nullable=False)

    secret_hash: Mapped[str | None] = mapped_column(Text(), nullable=True)

    identity_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    status: Mapped[IdentityStatus] = mapped_column(
        SQLEnum(IdentityStatus, name="identity_status"),
        nullable=False,
        default=IdentityStatus.PENDING,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    consecutive_failed_count: Mapped[int] = mapped_column(Integer(), default=0)

    user = relationship("User", back_populates="identities")
    sessions = relationship("Session", back_populates="identity")
    auth_events = relationship("AuthEvent", back_populates="identity")
