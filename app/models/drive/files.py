import enum
import uuid
from datetime import datetime

from sqlalchemy import BIGINT, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.database import Base


class FileStatus(enum.StrEnum):
    PENDING = "pending"
    READY = "ready"


class Files(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(100),
    )

    folder_id: Mapped[str | None] = mapped_column(
        ForeignKey("folders.id"),
        nullable=True,
    )

    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )

    storage_path: Mapped[str] = mapped_column(
        Text(),
    )

    size: Mapped[int] = mapped_column(
        BIGINT(),
    )

    extension: Mapped[str] = mapped_column(
        String(100),
    )

    thumbnail_path: Mapped[str | None] = mapped_column(
        Text(),
        nullable=True,
    )

    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=datetime.now,
    )

    status: Mapped[FileStatus] = mapped_column(nullable=False, default=FileStatus.PENDING)

    is_trashed: Mapped[bool] = mapped_column(nullable=False, default=False, index=True)
    trashed_at: Mapped[datetime | None] = mapped_column(
        DateTime(),
        nullable=True,
        default=None,
    )
    trashed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        default=None,
    )

    owner = relationship("User", foreign_keys=[owner_id])
    trashed_by = relationship("User", foreign_keys=[trashed_by_id], back_populates="trashed_files")
