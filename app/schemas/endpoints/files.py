import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.drive.files import FileStatus


class GenerateUploadLinkRequest(BaseModel):
    name: str
    user_id: str
    content_type: str
    folder_id: str | None = None


class MarkFileUploadRequest(BaseModel):
    id: uuid.UUID


class RenameFileRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class FileData(BaseModel):
    id: uuid.UUID
    name: str
    folder_id: str | None
    owner_id: uuid.UUID | None = None
    storage_path: str
    size: int
    extension: str
    status: FileStatus
    last_accessed_at: datetime
    created_at: datetime
    is_trashed: bool = False
    trashed_at: datetime | None = None


class FileUrlData(FileData):
    url: str


class FileActivityItem(BaseModel):
    action: str
    timestamp: datetime
    user_agent: str | None = None
    metadata: dict | None = None
    actor_id: uuid.UUID | None = None
    actor_type: str | None = None
    resource_id: str | None = None


class GenerateUploadLinkResponse(BaseModel):
    message: str
    data: dict[str, Any]


class MarkFileUploadResponse(BaseModel):
    message: str
    data: Any


class GetFileResponse(BaseModel):
    message: str
    data: FileData


class DownloadFileResponse(BaseModel):
    message: str
    data: FileUrlData | dict[str, Any]


class PreviewFileResponse(BaseModel):
    message: str
    data: FileUrlData | dict[str, Any]


class FileActivityResponse(BaseModel):
    message: str
    data: list[FileActivityItem]


class FileListResponse(BaseModel):
    message: str
    data: list[FileData]


class FileMessageResponse(BaseModel):
    message: str
    data: FileData


class EmptyTrashData(BaseModel):
    deleted_count: int


class EmptyTrashResponse(BaseModel):
    message: str
    data: EmptyTrashData
