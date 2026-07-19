from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.file import GenerateUploadLink, MarkFileUpload
from app.services.files import file_service

router = APIRouter(prefix="/files", tags=["File"])


@router.post("/gen_upload_link")
async def gen_upload_link(payload: GenerateUploadLink, db: AsyncSession = Depends(get_db)):
    service_response = await file_service.generate_pre_signed_url(
        name=payload.name,
        user_id=payload.user_id,
        folder_id=payload.folder_id,
        content_type=payload.content_type,
        db=db,
    )

    return {
        "message": "Link generated",
        "data": service_response,
    }


@router.post("/mark_upload_complete")
async def mark_upload_complete(payload: MarkFileUpload, db: AsyncSession = Depends(get_db)):
    service_response = await file_service.mark_upload_complete(id=payload.id, db=db)
    return {
        "message": "completed",
        "data": service_response,
    }
