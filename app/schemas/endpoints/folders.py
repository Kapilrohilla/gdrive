from typing import Any

from pydantic import BaseModel, Field


class CreateFolderRequest(BaseModel):
    parent_id: str | None = None
    owner_id: str
    name: str = Field(min_length=1)


class FolderMessageResponse(BaseModel):
    message: str
    data: Any
