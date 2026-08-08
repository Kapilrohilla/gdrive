import datetime
import uuid

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.types import Integer

from app.core.database.database import Base


class Folder(Base):
    __tablename__ = "folders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(100),
    )

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("folders.id"),
        nullable=True,
    )

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
    )

    file_count: Mapped[int] = mapped_column(Integer(), default=0)

    is_trashed: Mapped[bool] = mapped_column(nullable=False, default=False, index=True)
    trashed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(),
        nullable=True,
        default=None,
    )
    trashed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        default=None,
    )

    parent = relationship("Folder", remote_side="Folder.id", foreign_keys=[parent_id])
    owner = relationship("User", foreign_keys=[owner_id])
    trashed_by = relationship(
        "User", foreign_keys=[trashed_by_id], back_populates="trashed_folders"
    )
