import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConfigValueRequest(BaseModel):
    value: dict[str, Any]


class ConfigData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    value: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ConfigResponse(BaseModel):
    message: str
    data: ConfigData


class ConfigListResponse(BaseModel):
    message: str
    data: list[ConfigData]


class ConfigDeleteResponse(BaseModel):
    message: str
