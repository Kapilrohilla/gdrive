import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PermissionAction(str, Enum):
    READ = "read"
    SELECT = "select"
    CREATE = "create"
    IMPORT = "import"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE = "manage"


class PermissionBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    resource: str = Field(min_length=1, max_length=100)
    action: PermissionAction
    description: str | None = None


class CreatePermissionDto(PermissionBase):
    pass


class UpdatePermissionDto(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    resource: str | None = Field(default=None, min_length=1, max_length=100)
    action: PermissionAction | None = None
    description: str | None = None


class PermissionResponse(PermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
