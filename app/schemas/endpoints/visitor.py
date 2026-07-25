import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RegisterVisitorRequest(BaseModel):
    identifier_type: str = Field(min_length=1, max_length=100)
    identifier_value: str = Field(min_length=1, max_length=100)


class VisitorItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    identifier_type: str
    identifier_value: str
    user_id: uuid.UUID | None
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime


class RegisterVisitorResponse(BaseModel):
    token: str
    token_expired_at: datetime
    visitor: VisitorItemResponse


class GetVisitorsResponse(BaseModel):
    visitors: list[VisitorItemResponse]
    total: int
