import uuid

from pydantic import BaseModel

from app.schemas.iam.auth_event import AuthEventResponse
from app.schemas.iam.permission import (
    CreatePermissionDto,
    PermissionResponse,
    UpdatePermissionDto,
)
from app.schemas.iam.role import CreateRoleDto, RoleResponse, UpdateRoleDto
from app.schemas.iam.role_permission import (
    CreateRolePermissionDto,
    RolePermissionResponse,
)


class RoleListResponse(BaseModel):
    roles: list[RoleResponse]


class PermissionListResponse(BaseModel):
    permissions: list[PermissionResponse]


class RolePermissionListResponse(BaseModel):
    permissions: list[PermissionResponse]


class RolePermissionAssignRequest(BaseModel):
    permission_id: uuid.UUID


class MessageResponse(BaseModel):
    message: str


class MyPermissionsResponse(BaseModel):
    permissions: list[PermissionResponse]
