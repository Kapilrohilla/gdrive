import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class UserStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"


class RoleRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str


class UserBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    avatar: str | None = None
    status: UserStatus = UserStatus.ACTIVE
    role_id: uuid.UUID | None = None


class CreateUserDto(UserBase):
    pass


class UpdateUserDto(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=100)
    avatar: str | None = None
    status: UserStatus | None = None
    role_id: uuid.UUID | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: RoleRef | None = None
    created_at: datetime
    updated_at: datetime
