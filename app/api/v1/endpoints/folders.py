from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate
from app.schemas.endpoints.folders import CreateFolderRequest, FolderMessageResponse
from app.services.folder import folder_service

router = APIRouter(
    prefix="/folders",
    tags=["Folder"],
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
)


@router.post("/", response_model=FolderMessageResponse)
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


@router.get("/", response_model=FolderMessageResponse)
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
