import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.database import Base


class ShortUrls(Base):
    __tablename__ = "short_urls"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_url: Mapped[str] = mapped_column(Text())
    short_code: Mapped[str | None] = mapped_column(
        String(10), unique=True, nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    user = relationship("User", back_populates="short_urls")


__all__ = ["ShortUrls"]
