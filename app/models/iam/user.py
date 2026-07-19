import uuid
from enum import Enum

from sqlalchemy import Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

from app.core.database import Base


class UserStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"


class User(Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(100))

    avatar: Mapped[str | None] = mapped_column(Text(), nullable=True)

    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus, name="user_status"),
        default=UserStatus.ACTIVE,
    )

    role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=True,
    )

    role = relationship("Role", back_populates="users")
    identities = relationship("Identity", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    auth_events = relationship("AuthEvent", back_populates="user")
    visitors = relationship("Visitor", back_populates="user")
