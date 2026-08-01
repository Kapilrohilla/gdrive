from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate, require_permission
from app.models.iam.permission import PermissionAction
from app.schemas.endpoints.files import (
    DownloadFileResponse,
    FileActivityResponse,
    FileListResponse,
    GenerateUploadLinkRequest,
    GenerateUploadLinkResponse,
    GetFileResponse,
    MarkFileUploadRequest,
    MarkFileUploadResponse,
    PreviewFileResponse,
)
from app.services.drive.file_resource_event import FileResourceEventService
from app.services.drive.files import FileService, serialize_file
from app.services.resource_events import ResourceEventService

router = APIRouter(
    prefix="/files",
    tags=["File"],
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
)

file_service = FileService()
resource_event_service = ResourceEventService()
file_resource_event_service = FileResourceEventService(
    file_service=file_service,
    resource_event_service=resource_event_service,
)


@router.post(
    "/gen_upload_link",
    dependencies=[Depends(require_permission("files", PermissionAction.CREATE))],
    response_model=GenerateUploadLinkResponse,
)
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


@router.post(
    "/mark_upload_complete",
    dependencies=[Depends(require_permission("files", PermissionAction.UPDATE))],
    response_model=MarkFileUploadResponse,
)
async def mark_upload_complete(payload: MarkFileUploadRequest, db: DbSession):
    service_response = await file_service.mark_upload_complete(id=payload.id, db=db)
    return {
        "message": "completed",
        "data": service_response,
    }


@router.get(
    "/",
    dependencies=[Depends(require_permission("files", PermissionAction.READ))],
    response_model=FileListResponse,
)
async def list_files(db: DbSession, folder_id: str | None = None):
    files = await file_service.get_files(db=db, folder_id=folder_id)
    return {
        "message": "files retrieved",
        "data": [serialize_file(file) for file in files],
    }


@router.get(
    "/{file_id}",
    dependencies=[Depends(require_permission("files", PermissionAction.READ))],
    response_model=GetFileResponse,
)
async def get_file(file_id: UUID, db: DbSession):
    file = await file_service.get_file(db=db, id=file_id)
    return {
        "message": "file retrieved",
        "data": serialize_file(file),
    }


@router.get(
    "/{file_id}/download",
    dependencies=[Depends(require_permission("files", PermissionAction.READ))],
    response_model=DownloadFileResponse,
)
async def download_file(file_id: UUID, db: DbSession, request: Request):
    service_response = await file_service.download_file_url(
        db=db,
        id=file_id,
        user_agent=request.headers.get("user-agent"),
    )
    return {
        "message": "file downloaded",
        "data": service_response,
    }


@router.get(
    "/{file_id}/preview",
    dependencies=[Depends(require_permission("files", PermissionAction.READ))],
    response_model=PreviewFileResponse,
)
async def preview_file(file_id: UUID, db: DbSession, request: Request):
    service_response = await file_service.preview_file_url(
        db=db,
        id=file_id,
        user_agent=request.headers.get("user-agent"),
    )
    return {
        "message": "file previewed",
        "data": service_response,
    }


@router.get(
    "/{file_id}/activity",
    dependencies=[Depends(require_permission("files", PermissionAction.READ))],
    response_model=FileActivityResponse,
)
async def get_file_activity(file_id: UUID, db: DbSession):
    service_response = await file_resource_event_service.get_file_activity(
        db=db,
        file_id=file_id,
    )
    return {
        "message": "file activity retrieved",
        "data": service_response,
    }


__all__ = ["router"]
