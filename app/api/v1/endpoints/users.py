import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Request

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate, require_permission
from app.models.iam.permission import PermissionAction
from app.schemas.endpoints.users import (
    CreateUserRequest,
    CreateUserResponse,
    GetUserProfileResponse,
)
from app.services.user import user_service

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
)


@router.get(
    "/",
    dependencies=[Depends(require_permission("users", PermissionAction.READ))],
)
async def get_users(db: DbSession):
    users = await user_service.get_user(db)
    return users


@router.post(
    "/",
    dependencies=[Depends(require_permission("users", PermissionAction.CREATE))],
    response_model=CreateUserResponse,
)
async def create_user(payload: CreateUserRequest, db: DbSession):
    data = await user_service.create_user(db=db, full_name=payload.full_name)
    return {"message": "User created", "data": data, "timestamp": datetime.now()}


@router.get(
    "/profile",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=GetUserProfileResponse,
)
async def get_user_profile(request: Request, db: DbSession):
    profile = await user_service.get_user_profile(
        db=db,
        user_id=request.state.user_id,
        identity_id=request.state.identity_id,
    )
    return {"message": "User profile", "data": profile, "timestamp": datetime.now()}


__all__ = ["router"]
