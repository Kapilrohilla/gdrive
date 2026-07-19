import uuid
from enum import Enum

from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuthEventSubject(str, Enum):
    LOGIN_SUCCESS = "login success"
    LOGIN_FAILED = "login failed"
    LOGOUT = "logout"
    PASSWORD_CHANGED = "password changed"
    PASSWORD_RESET = "password reset"
    EMAIL_VERIFIED = "email verified"
    OTP_SENT = "otp sent"
    OTP_VERIFIED = "otp verified"
    SESSION_CREATED = "session created"
    SESSION_REVOKED = "session revoked"
    ACCOUNT_LOCKED = "account locked"


class AuthEvent(Base):
    __tablename__ = "auth_events"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    identity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identities.id"),
        nullable=True,
    )

    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id"),
        nullable=True,
    )

    subject: Mapped[AuthEventSubject] = mapped_column(
        SQLEnum(AuthEventSubject, name="auth_event_subject"),
        nullable=False,
    )

    success: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    failure_reason: Mapped[str | None] = mapped_column(Text(), nullable=True)

    user = relationship("User", back_populates="auth_events")
    identity = relationship("Identity", back_populates="auth_events")
    session = relationship("Session", back_populates="auth_events")
