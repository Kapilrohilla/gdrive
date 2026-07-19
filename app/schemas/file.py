import uuid

from pydantic import BaseModel


class GenerateUploadLink(BaseModel):
    name: str
    user_id: str
    content_type: str
    folder_id: str | None = None


class MarkFileUpload(BaseModel):
    id: uuid.UUID
