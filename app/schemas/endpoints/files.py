import uuid
from typing import Any

from pydantic import BaseModel, Field


class GenerateUploadLinkRequest(BaseModel):
    name: str
    user_id: str
    content_type: str
    folder_id: str | None = None


class MarkFileUploadRequest(BaseModel):
    id: uuid.UUID


class GenerateUploadLinkResponse(BaseModel):
    message: str
    data: dict[str, Any]


class MarkFileUploadResponse(BaseModel):
    message: str
    data: Any
