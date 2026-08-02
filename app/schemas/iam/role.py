import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RoleBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    is_system: bool = True
    is_standard: bool = False


class CreateRoleDto(RoleBase):
    pass


class UpdateRoleDto(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    is_system: bool | None = None
    is_standard: bool | None = None


class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
