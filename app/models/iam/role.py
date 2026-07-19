from sqlalchemy import Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    is_system: Mapped[bool] = mapped_column(Boolean(), default=True)

    users = relationship("User", back_populates="role")
    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        viewonly=True,
    )
