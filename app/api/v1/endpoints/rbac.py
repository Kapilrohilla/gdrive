from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
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

router = APIRouter(prefix="/rbac", tags=["RBAC"])

rbac_service = RbacService()


@router.get(
    "/roles",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=RoleListResponse,
)
async def list_roles(db: AsyncSession = Depends(get_db)):
    roles = await rbac_service.list_roles(db)
    return {"roles": roles}


@router.post(
    "/roles",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=RoleResponse,
)
async def create_role(payload: CreateRoleDto, db: AsyncSession = Depends(get_db)):
    role = await rbac_service.create_role(payload, db)
    await db.commit()
    return role


@router.get(
    "/roles/{role_id}",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=RoleResponse,
)
async def get_role(role_id: UUID, db: AsyncSession = Depends(get_db)):
    role = await rbac_service.get_role(role_id, db)
    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.patch(
    "/roles/{role_id}",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=RoleResponse,
)
async def update_role(
    role_id: UUID, payload: UpdateRoleDto, db: AsyncSession = Depends(get_db)
):
    role = await rbac_service.update_role(role_id, payload, db)
    await db.commit()
    return role


@router.delete(
    "/roles/{role_id}",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=MessageResponse,
)
async def delete_role(role_id: UUID, db: AsyncSession = Depends(get_db)):
    await rbac_service.delete_role(role_id, db)
    await db.commit()
    return {"message": "Role deleted successfully"}


@router.get(
    "/permissions",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=PermissionListResponse,
)
async def list_permissions(db: AsyncSession = Depends(get_db)):
    permissions = await rbac_service.list_permissions(db)
    return {"permissions": permissions}


@router.post(
    "/permissions",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=PermissionResponse,
)
async def create_permission(
    payload: CreatePermissionDto, db: AsyncSession = Depends(get_db)
):
    permission = await rbac_service.create_permission(payload, db)
    await db.commit()
    return permission


@router.get(
    "/permissions/{permission_id}",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=PermissionResponse,
)
async def get_permission(permission_id: UUID, db: AsyncSession = Depends(get_db)):
    permission = await rbac_service.get_permission(permission_id, db)
    if permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.patch(
    "/permissions/{permission_id}",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=PermissionResponse,
)
async def update_permission(
    permission_id: UUID,
    payload: UpdatePermissionDto,
    db: AsyncSession = Depends(get_db),
):
    permission = await rbac_service.update_permission(permission_id, payload, db)
    await db.commit()
    return permission


@router.delete(
    "/permissions/{permission_id}",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=MessageResponse,
)
async def delete_permission(permission_id: UUID, db: AsyncSession = Depends(get_db)):
    await rbac_service.delete_permission(permission_id, db)
    await db.commit()
    return {"message": "Permission deleted successfully"}


@router.get(
    "/roles/{role_id}/permissions",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=RolePermissionListResponse,
)
async def list_role_permissions(role_id: UUID, db: AsyncSession = Depends(get_db)):
    permissions = await rbac_service.list_role_permissions(role_id, db)
    return {"permissions": permissions}


@router.post(
    "/roles/{role_id}/permissions",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=RolePermissionResponse,
)
async def assign_permission_to_role(
    role_id: UUID,
    payload: RolePermissionAssignRequest,
    db: AsyncSession = Depends(get_db),
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
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=MessageResponse,
)
async def remove_permission_from_role(
    role_id: UUID, permission_id: UUID, db: AsyncSession = Depends(get_db)
):
    await rbac_service.remove_permission_from_role(role_id, permission_id, db)
    await db.commit()
    return {"message": "Permission removed from role successfully"}


@router.get(
    "/me/permissions",
    dependencies=[Depends(authenticate(TokenType.ACCESS))],
    response_model=MyPermissionsResponse,
)
async def get_my_permissions(request: Request, db: AsyncSession = Depends(get_db)):
    permissions = await rbac_service.get_user_permissions(
        user_id=UUID(str(request.state.user_id)),
        db=db,
    )
    return {"permissions": permissions}
