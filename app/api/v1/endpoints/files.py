from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate
from app.schemas.endpoints.files import (
    GenerateUploadLinkRequest,
    GenerateUploadLinkResponse,
    MarkFileUploadRequest,
    MarkFileUploadResponse,
)
from app.services.files import file_service

router = APIRouter(
    prefix="/files",
    tags=["File"],
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
)


@router.post("/gen_upload_link", response_model=GenerateUploadLinkResponse)
async def gen_upload_link(payload: GenerateUploadLinkRequest, db: DbSession):
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


@router.post("/mark_upload_complete", response_model=MarkFileUploadResponse)
async def mark_upload_complete(payload: MarkFileUploadRequest, db: DbSession):
    service_response = await file_service.mark_upload_complete(id=payload.id, db=db)
    return {
        "message": "completed",
        "data": service_response,
    }
