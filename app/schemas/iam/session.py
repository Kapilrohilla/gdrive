import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SessionBase(BaseModel):
    user_id: uuid.UUID
    identity_id: uuid.UUID
    refresh_token_hash: str
    device_name: str | None = Field(default=None, max_length=200)
    browser: str | None = Field(default=None, max_length=200)
    os: str | None = Field(default=None, max_length=200)
    ip: str | None = Field(default=None, max_length=100)
    user_agent: str | None = Field(default=None, max_length=500)
    expires_at: datetime | None = None


class CreateSessionDto(SessionBase):
    pass


class UpdateSessionDto(BaseModel):
    device_name: str | None = Field(default=None, max_length=200)
    browser: str | None = Field(default=None, max_length=200)
    os: str | None = Field(default=None, max_length=200)
    ip: str | None = Field(default=None, max_length=100)
    user_agent: str | None = Field(default=None, max_length=500)
    last_seen_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None


class SessionResponse(SessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    last_seen_at: datetime
    revoked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
