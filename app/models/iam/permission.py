from enum import Enum

from sqlalchemy import Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

from app.core.database import Base


class PermissionAction(str, Enum):
    READ = "read"
    SELECT = "select"
    CREATE = "create"
    IMPORT = "import"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE = "manage"


class Permission(Base):
    __tablename__ = "permissions"

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    resource: Mapped[str] = mapped_column(String(100), nullable=False)

    action: Mapped[PermissionAction] = mapped_column(
        SQLEnum(PermissionAction, name="permission_action"),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )
    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        viewonly=True,
    )
