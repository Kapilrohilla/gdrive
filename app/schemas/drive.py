from pydantic import BaseModel


class CreateFolderPayload(BaseModel):
    name: str
    parent_id: str | None = None


class UploadPayload(BaseModel):
    name: str
