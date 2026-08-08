from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate, require_permission
from app.models.iam.permission import PermissionAction
from app.schemas.endpoints.folders import (
    CreateFolderRequest,
    CreateFolderResponse,
    EmptyTrashResponse,
    FolderListResponse,
    FolderMessageResponse,
    RenameFolderRequest,
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


@router.get(
    "/trash",
    dependencies=[Depends(require_permission("folders", PermissionAction.READ))],
    response_model=FolderListResponse,
)
async def list_trashed_folders(request: Request, db: DbSession):
    owner_id = UUID(str(request.state.user_id))
    folders = await folder_service.get_trashed_folders(owner_id=owner_id, db=db)
    return {
        "message": "Trashed folders fetched successfully",
        "data": folders,
    }


@router.delete(
    "/trash",
    dependencies=[Depends(require_permission("folders", PermissionAction.DELETE))],
    response_model=EmptyTrashResponse,
)
async def empty_trash_folders(request: Request, db: DbSession):
    owner_id = UUID(str(request.state.user_id))
    deleted_count = await folder_service.empty_trash(owner_id=owner_id, db=db)
    return {
        "message": "trash emptied",
        "data": {"deleted_count": deleted_count},
    }


@router.patch(
    "/{folder_id}/rename",
    dependencies=[Depends(require_permission("folders", PermissionAction.UPDATE))],
    response_model=FolderMessageResponse,
)
async def rename_folder(
    folder_id: UUID,
    payload: RenameFolderRequest,
    request: Request,
    db: DbSession,
):
    owner_id = UUID(str(request.state.user_id))
    folder = await folder_service.rename_folder(
        folder_id=folder_id,
        name=payload.name,
        owner_id=owner_id,
        db=db,
    )
    item_count = await folder_service._count_folder_items(folder.id, db)
    return {
        "message": "Folder renamed",
        "data": serialize_folder(folder, item_count=item_count),
    }


@router.post(
    "/{folder_id}/trash",
    dependencies=[Depends(require_permission("folders", PermissionAction.DELETE))],
    response_model=FolderMessageResponse,
)
async def trash_folder(folder_id: UUID, request: Request, db: DbSession):
    user_id = UUID(str(request.state.user_id))
    folder = await folder_service.trash_folder(folder_id=folder_id, user_id=user_id, db=db)
    return {
        "message": "Folder moved to trash",
        "data": serialize_folder(folder),
    }


@router.post(
    "/{folder_id}/restore",
    dependencies=[Depends(require_permission("folders", PermissionAction.UPDATE))],
    response_model=FolderMessageResponse,
)
async def restore_folder(folder_id: UUID, request: Request, db: DbSession):
    user_id = UUID(str(request.state.user_id))
    folder = await folder_service.restore_folder(folder_id=folder_id, user_id=user_id, db=db)
    item_count = await folder_service._count_folder_items(folder.id, db)
    return {
        "message": "Folder restored",
        "data": serialize_folder(folder, item_count=item_count),
    }


__all__ = ["router"]
