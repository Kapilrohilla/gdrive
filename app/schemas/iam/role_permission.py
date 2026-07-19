import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RolePermissionBase(BaseModel):
    role_id: uuid.UUID
    permission_id: uuid.UUID


class CreateRolePermissionDto(RolePermissionBase):
    pass


class RolePermissionResponse(RolePermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
