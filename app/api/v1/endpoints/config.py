from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate, require_permission
from app.models.iam.permission import PermissionAction
from app.schemas.endpoints.config import (
    ConfigDeleteResponse,
    ConfigListResponse,
    ConfigResponse,
    ConfigValueRequest,
)
from app.services.platform.config import ConfigService

router = APIRouter(
    prefix="/config",
    tags=["Config"],
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
)

config_service = ConfigService()


@router.get(
    "/",
    dependencies=[Depends(require_permission("config", PermissionAction.READ))],
    response_model=ConfigListResponse,
)
async def list_configs(db: DbSession):
    configs = await config_service.list_configs(db)
    return {
        "message": "configs retrieved",
        "data": configs,
    }


@router.get(
    "/{key}",
    dependencies=[Depends(require_permission("config", PermissionAction.READ))],
    response_model=ConfigResponse,
)
async def get_config(key: str, db: DbSession):
    config = await config_service.get_config(db, key)
    return {
        "message": "config retrieved",
        "data": config,
    }


@router.put(
    "/{key}",
    dependencies=[Depends(require_permission("config", PermissionAction.UPDATE))],
    response_model=ConfigResponse,
)
async def upsert_config(key: str, payload: ConfigValueRequest, db: DbSession):
    config = await config_service.upsert_config(db, key=key, value=payload.value)
    return {
        "message": "config saved",
        "data": config,
    }


@router.delete(
    "/{key}",
    dependencies=[Depends(require_permission("config", PermissionAction.DELETE))],
    response_model=ConfigDeleteResponse,
)
async def delete_config(key: str, db: DbSession):
    await config_service.delete_config(db, key)
    return {"message": "config deleted"}


__all__ = ["router"]
