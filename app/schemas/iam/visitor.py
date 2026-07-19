import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class VisitorBase(BaseModel):
    visitor_id: str = Field(min_length=1, max_length=100)
    user_agent: str | None = Field(default=None, max_length=500)
    metadata_json: dict[str, Any] | None = None
    user_id: uuid.UUID | None = None


class CreateVisitorDto(VisitorBase):
    pass


class UpdateVisitorDto(BaseModel):
    user_agent: str | None = Field(default=None, max_length=500)
    metadata_json: dict[str, Any] | None = None
    user_id: uuid.UUID | None = None
    last_seen_at: datetime | None = None


class VisitorResponse(VisitorBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime
