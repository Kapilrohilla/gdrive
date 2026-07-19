import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class IdentityProvider(str, Enum):
    PASSWORD = "password"
    MAGIC_LINK = "magic_link"
    OTP = "otp"


class IdentityStatus(str, Enum):
    PENDING = "verification_pending"
    ACTIVE = "active"
    BLOCKED = "blocked"


class IdentityBase(BaseModel):
    provider: IdentityProvider
    user_id: uuid.UUID
    identifier: str = Field(min_length=1, max_length=500)
    status: IdentityStatus = IdentityStatus.PENDING


class CreateIdentityDto(IdentityBase):
    secret_hash: str | None = None


class UpdateIdentityDto(BaseModel):
    identifier: str | None = Field(default=None, min_length=1, max_length=500)
    secret_hash: str | None = None
    status: IdentityStatus | None = None
    identity_verified_at: datetime | None = None
    last_login_at: datetime | None = None
    locked_until: datetime | None = None
    consecutive_failed_count: int | None = None


class IdentityResponse(IdentityBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    secret_hash: str | None = None
    identity_verified_at: datetime | None = None
    last_login_at: datetime | None = None
    locked_until: datetime | None = None
    consecutive_failed_count: int
    created_at: datetime
    updated_at: datetime
