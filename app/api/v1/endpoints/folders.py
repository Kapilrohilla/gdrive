from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate, require_permission
from app.models.iam.permission import PermissionAction
from app.schemas.endpoints.folders import CreateFolderRequest, FolderMessageResponse
from app.services.drive.folder import FolderService

router = APIRouter(
    prefix="/folders",
    tags=["Folder"],
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
)

folder_service = FolderService()


@router.post(
    "/",
    dependencies=[Depends(require_permission("folders", PermissionAction.CREATE))],
    response_model=FolderMessageResponse,
)
async def create_folder(payload: CreateFolderRequest, db: DbSession):
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


@router.get(
    "/",
    dependencies=[Depends(require_permission("folders", PermissionAction.READ))],
    response_model=FolderMessageResponse,
)
async def get_folder(
    db: DbSession,
    user_id: str | None = None,
    parent_id: str | None = None,
):
    service_response = await folder_service.get_folder(user_id, parent_id, db)

    return {
        "message": "Fetched successfully",
        "data": service_response,
    }


__all__ = ["router"]
