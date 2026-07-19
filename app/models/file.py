from enum import Enum
import uuid

from sqlalchemy import BIGINT, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FileStatus(str, Enum):
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

    folder_id: Mapped[str] = mapped_column(
        ForeignKey("folders.id"),
    )

    s3_path: Mapped[str] = mapped_column(
        Text(),
    )

    size: Mapped[int] = mapped_column(
        BIGINT(),
    )

    extension: Mapped[str] = mapped_column(
        String(100),
    )

    status: Mapped[FileStatus] = mapped_column(nullable=False, default=FileStatus.PENDING)
    folder = relationship("Folder")
