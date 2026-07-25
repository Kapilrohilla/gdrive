from typing import Any

from pydantic import BaseModel, Field


class CreateFolderPayload(BaseModel):
    name: str = Field(min_length=1)
    parent_id: str | None = None


class UploadPayload(BaseModel):
    name: str = Field(min_length=1)


class DriveDataResponse(BaseModel):
    data: Any


class DriveMessageResponse(BaseModel):
    data: dict[str, Any]
