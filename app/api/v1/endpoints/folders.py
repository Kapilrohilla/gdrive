from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate, require_permission
from app.models.iam.permission import PermissionAction
from app.schemas.endpoints.folders import (
    CreateFolderRequest,
    CreateFolderResponse,
    FolderListResponse,
)
from app.services.drive.folder import FolderService, serialize_folder

router = APIRouter(
    prefix="/folders",
    tags=["Folder"],
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
)

folder_service = FolderService()


@router.post(
    "/",
    dependencies=[Depends(require_permission("folders", PermissionAction.CREATE))],
    response_model=CreateFolderResponse,
)
async def create_folder(request: Request, payload: CreateFolderRequest, db: DbSession):
    owner_id = UUID(str(request.state.user_id))
    folder = await folder_service.create_folder(
        name=payload.name,
        owner_id=owner_id,
        parent_id=payload.parent_id,
        db=db,
    )
    await db.commit()
    await db.refresh(folder)
    item_count = await folder_service._count_folder_items(folder.id, db)
    return {
        "message": "Folder created",
        "data": serialize_folder(folder, item_count=item_count),
    }


@router.get(
    "/",
    dependencies=[Depends(require_permission("folders", PermissionAction.READ))],
    response_model=FolderListResponse,
)
async def get_folders(
    request: Request,
    db: DbSession,
    parent_id: UUID | None = None,
):
    owner_id = UUID(str(request.state.user_id))
    folders = await folder_service.get_folders(
        owner_id=owner_id,
        parent_id=parent_id,
        db=db,
    )
    return {
        "message": "Folders fetched successfully",
        "data": folders,
    }


__all__ = ["router"]
