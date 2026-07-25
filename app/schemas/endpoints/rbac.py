import uuid

from pydantic import BaseModel

from app.schemas.iam.permission import PermissionResponse
from app.schemas.iam.role import RoleResponse


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
