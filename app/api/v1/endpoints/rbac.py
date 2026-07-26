from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.deps import DbSession
from app.constants.enum import TokenType
from app.middleware import authenticate
from app.schemas.endpoints.rbac import (
    MessageResponse,
    MyPermissionsResponse,
    PermissionListResponse,
    RoleListResponse,
    RolePermissionAssignRequest,
    RolePermissionListResponse,
)
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
from app.services.iam.rbac import RbacService

router = APIRouter(
    prefix="/rbac",
    tags=["RBAC"],
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
)

rbac_service = RbacService()


@router.get("/roles", response_model=RoleListResponse)
async def list_roles(db: DbSession):
    roles = await rbac_service.list_roles(db)
    return {"roles": roles}


@router.post("/roles", response_model=RoleResponse)
async def create_role(payload: CreateRoleDto, db: DbSession):
    role = await rbac_service.create_role(payload, db)
    await db.commit()
    return role


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: UUID, db: DbSession):
    role = await rbac_service.get_role(role_id, db)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: UUID, payload: UpdateRoleDto, db: DbSession):
    role = await rbac_service.update_role(role_id, payload, db)
    await db.commit()
    return role


@router.delete("/roles/{role_id}", response_model=MessageResponse)
async def delete_role(role_id: UUID, db: DbSession):
    await rbac_service.delete_role(role_id, db)
    await db.commit()
    return {"message": "Role deleted successfully"}


@router.get("/permissions", response_model=PermissionListResponse)
async def list_permissions(db: DbSession):
    permissions = await rbac_service.list_permissions(db)
    return {"permissions": permissions}


@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(payload: CreatePermissionDto, db: DbSession):
    permission = await rbac_service.create_permission(payload, db)
    await db.commit()
    return permission


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(permission_id: UUID, db: DbSession):
    permission = await rbac_service.get_permission(permission_id, db)
    if permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.patch("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(permission_id: UUID, payload: UpdatePermissionDto, db: DbSession):
    permission = await rbac_service.update_permission(permission_id, payload, db)
    await db.commit()
    return permission


@router.delete("/permissions/{permission_id}", response_model=MessageResponse)
async def delete_permission(permission_id: UUID, db: DbSession):
    await rbac_service.delete_permission(permission_id, db)
    await db.commit()
    return {"message": "Permission deleted successfully"}


@router.get("/roles/{role_id}/permissions", response_model=RolePermissionListResponse)
async def list_role_permissions(role_id: UUID, db: DbSession):
    permissions = await rbac_service.list_role_permissions(role_id, db)
    return {"permissions": permissions}


@router.post("/roles/{role_id}/permissions", response_model=RolePermissionResponse)
async def assign_permission_to_role(
    role_id: UUID,
    payload: RolePermissionAssignRequest,
    db: DbSession,
):
    role_permission = await rbac_service.assign_permission_to_role(
        role_id=role_id,
        payload=CreateRolePermissionDto(
            role_id=role_id,
            permission_id=payload.permission_id,
        ),
        db=db,
    )
    await db.commit()
    return role_permission


@router.delete(
    "/roles/{role_id}/permissions/{permission_id}",
    response_model=MessageResponse,
)
async def remove_permission_from_role(role_id: UUID, permission_id: UUID, db: DbSession):
    await rbac_service.remove_permission_from_role(role_id, permission_id, db)
    await db.commit()
    return {"message": "Permission removed from role successfully"}


@router.get("/me/permissions", response_model=MyPermissionsResponse)
async def get_my_permissions(request: Request, db: DbSession):
    permissions = await rbac_service.get_user_permissions(
        user_id=UUID(str(request.state.user_id)),
        db=db,
    )
    return {"permissions": permissions}
