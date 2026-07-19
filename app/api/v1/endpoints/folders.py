from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.folder import CreateFolderDto
from app.services.folder import folder_service

router = APIRouter(prefix="/folders", tags=["Folder"])


@router.post("/")
async def create_folder(payload: CreateFolderDto, db: AsyncSession = Depends(get_db)):
    service_response = await folder_service.create_folder(
        name=payload.name,
        owner_id=payload.owner_id,
        parent_id=payload.parent_id,
        db=db,
    )

    return {
        "message": "created successful",
        "data": service_response,
    }


@router.get("/")
async def get_folder(
    user_id: str | None = None,
    parent_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    service_response = await folder_service.get_folder(user_id, parent_id, db)

    return {
        "message": "Fetched successfully",
        "data": service_response,
    }
