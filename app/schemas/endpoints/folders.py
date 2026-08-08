import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateFolderRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    parent_id: uuid.UUID | None = None


class RenameFolderRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class FolderData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    parent_id: uuid.UUID | None
    owner_id: uuid.UUID
    file_count: int
    created_at: datetime
    updated_at: datetime
    is_trashed: bool = False
    trashed_at: datetime | None = None


class CreateFolderResponse(BaseModel):
    message: str
    data: FolderData


class FolderListResponse(BaseModel):
    message: str
    data: list[FolderData]


class FolderMessageResponse(BaseModel):
    message: str
    data: FolderData


class EmptyTrashData(BaseModel):
    deleted_count: int


class EmptyTrashResponse(BaseModel):
    message: str
    data: EmptyTrashData
