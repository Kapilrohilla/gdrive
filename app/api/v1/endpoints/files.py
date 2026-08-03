from uuid import UUID

from fastapi import APIRouter, Depends, Request

import app.core.logger as logger
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
    "/initialize_upload",
    dependencies=[Depends(require_permission("files", PermissionAction.CREATE))],
    response_model=GenerateUploadLinkResponse,
)
async def initialize_upload(payload: GenerateUploadLinkRequest, db: DbSession):
    service_response = await file_service.initialize_upload(
        name=payload.name,
        user_id=payload.user_id,
        folder_id=payload.folder_id,
        content_type=payload.content_type,
        db=db,
    )

    logger.info(f"Link generated: {service_response}")
    print(f"Link generated: {service_response}")
    return {
        "message": "Link generated",
        "data": service_response,
    }


@router.post(
    "/complete_upload",
    dependencies=[Depends(require_permission("files", PermissionAction.UPDATE))],
    response_model=MarkFileUploadResponse,
)
async def complete_upload(payload: MarkFileUploadRequest, db: DbSession):
    service_response = await file_service.complete_upload(id=payload.id, db=db)
    return {
        "message": "completed",
        "data": service_response,
    }


@router.get(
    "/",
    dependencies=[Depends(require_permission("files", PermissionAction.READ))],
    response_model=FileListResponse,
)
async def list_files(db: DbSession, folder_id: UUID | None = None):
    files = await file_service.get_files(db=db, folder_id=folder_id)
    return {
        "message": "files retrieved",
        "data": [serialize_file(file) for file in files],
    }


@router.get(
    "/me/activity",
    dependencies=[Depends(require_permission("my_file_activity", PermissionAction.READ))],
    response_model=FileActivityResponse,
)
async def get_my_file_activity(request: Request, db: DbSession):
    user_id = UUID(str(request.state.user_id))
    service_response = await file_resource_event_service.get_my_file_activity(
        db=db,
        user_id=user_id,
    )
    return {
        "message": "my file activity retrieved",
        "data": service_response,
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
    dependencies=[Depends(require_permission("files", PermissionAction.SELECT))],
    response_model=DownloadFileResponse,
)
async def download_file(file_id: UUID, db: DbSession, request: Request):
    user_id = UUID(str(request.state.user_id))
    service_response = await file_service.download_file_url(
        db=db,
        id=file_id,
        user_agent=request.headers.get("user-agent"),
        actor_id=user_id,
    )
    return {
        "message": "file downloaded",
        "data": service_response,
    }


@router.get(
    "/{file_id}/preview",
    dependencies=[Depends(require_permission("files", PermissionAction.SELECT))],
    response_model=PreviewFileResponse,
)
async def preview_file(file_id: UUID, db: DbSession, request: Request):
    user_id = UUID(str(request.state.user_id))
    service_response = await file_service.preview_file_url(
        db=db,
        id=file_id,
        user_agent=request.headers.get("user-agent"),
        actor_id=user_id,
    )
    return {
        "message": "file previewed",
        "data": service_response,
    }


@router.get(
    "/{file_id}/activity",
    dependencies=[Depends(require_permission("file_activity", PermissionAction.READ))],
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
