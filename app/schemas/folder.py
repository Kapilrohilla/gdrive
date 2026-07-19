from pydantic import BaseModel


class CreateFolderDto(BaseModel):
    parent_id: str | None = None
    owner_id: str
    name: str
