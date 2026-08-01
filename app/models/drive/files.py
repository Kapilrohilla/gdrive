import enum
import uuid
from datetime import datetime

from sqlalchemy import BIGINT, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

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

    storage_path: Mapped[str] = mapped_column(
        Text(),
    )

    size: Mapped[int] = mapped_column(
        BIGINT(),
    )

    extension: Mapped[str] = mapped_column(
        String(100),
    )

    # will be used to transfer storage_type from on-demand to glacier storage path
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(),
        default=datetime.now,
    )

    status: Mapped[FileStatus] = mapped_column(nullable=False, default=FileStatus.PENDING)