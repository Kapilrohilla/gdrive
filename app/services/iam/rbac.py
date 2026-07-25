import uuid

from app.models.iam.permission import Permission
from app.models.iam.role import Role
from app.models.iam.role_permission import RolePermission
from app.models.iam.user import User
from app.schemas.iam.permission import CreatePermissionDto, UpdatePermissionDto
from app.schemas.iam.role import CreateRoleDto, UpdateRoleDto
from app.schemas.iam.role_permission import CreateRolePermissionDto
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class RbacService:
    async def list_roles(self, db: AsyncSession) -> list[Role]:
        stmt = select(Role).order_by(Role.name)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_role(self, role_id: uuid.UUID, db: AsyncSession) -> Role | None:
        stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_role(self, payload: CreateRoleDto, db: AsyncSession) -> Role:
        role = Role(
            name=payload.name,
            description=payload.description,
            is_system=payload.is_system,
        )
        db.add(role)
        await db.flush()
        await db.refresh(role)
        return role

    async def update_role(
        self, role_id: uuid.UUID, payload: UpdateRoleDto, db: AsyncSession
    ) -> Role:
        role = await self.get_role(role_id, db)
        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")

        if payload.name is not None:
            role.name = payload.name
        if payload.description is not None:
            role.description = payload.description
        if payload.is_system is not None:
            role.is_system = payload.is_system

        db.add(role)
        await db.flush()
        await db.refresh(role)
        return role

    async def delete_role(self, role_id: uuid.UUID, db: AsyncSession) -> None:
        role = await self.get_role(role_id, db)
        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")
        if role.is_system:
            raise HTTPException(
                status_code=400, detail="System roles cannot be deleted"
            )

        db.delete(role)
        await db.flush()

    async def list_permissions(self, db: AsyncSession) -> list[Permission]:
        stmt = select(Permission).order_by(Permission.resource, Permission.action)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_permission(
        self, permission_id: uuid.UUID, db: AsyncSession
    ) -> Permission | None:
        stmt = select(Permission).where(Permission.id == permission_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_permission(
        self, payload: CreatePermissionDto, db: AsyncSession
    ) -> Permission:
        permission = Permission(
            name=payload.name,
            resource=payload.resource,
            action=payload.action,
            description=payload.description,
        )
        db.add(permission)
        await db.flush()
        await db.refresh(permission)
        return permission

    async def update_permission(
        self, permission_id: uuid.UUID, payload: UpdatePermissionDto, db: AsyncSession
    ) -> Permission:
        permission = await self.get_permission(permission_id, db)
        if permission is None:
            raise HTTPException(status_code=404, detail="Permission not found")

        if payload.name is not None:
            permission.name = payload.name
        if payload.resource is not None:
            permission.resource = payload.resource
        if payload.action is not None:
            permission.action = payload.action
        if payload.description is not None:
            permission.description = payload.description

        db.add(permission)
        await db.flush()
        await db.refresh(permission)
        return permission

    async def delete_permission(
        self, permission_id: uuid.UUID, db: AsyncSession
    ) -> None:
        permission = await self.get_permission(permission_id, db)
        if permission is None:
            raise HTTPException(status_code=404, detail="Permission not found")

        db.delete(permission)
        await db.flush()

    async def list_role_permissions(
        self, role_id: uuid.UUID, db: AsyncSession
    ) -> list[Permission]:
        role = await self.get_role(role_id, db)
        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")
        return list(role.permissions)

    async def assign_permission_to_role(
        self, role_id: uuid.UUID, payload: CreateRolePermissionDto, db: AsyncSession
    ) -> RolePermission:
        role = await self.get_role(role_id, db)
        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")

        permission = await self.get_permission(payload.permission_id, db)
        if permission is None:
            raise HTTPException(status_code=404, detail="Permission not found")

        if payload.role_id != role_id:
            raise HTTPException(status_code=400, detail="Role ID mismatch")

        existing_stmt = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == payload.permission_id,
        )
        existing = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing is not None:
            return existing

        role_permission = RolePermission(
            role_id=role_id,
            permission_id=payload.permission_id,
        )
        db.add(role_permission)
        await db.flush()
        await db.refresh(role_permission)
        return role_permission

    async def remove_permission_from_role(
        self, role_id: uuid.UUID, permission_id: uuid.UUID, db: AsyncSession
    ) -> None:
        stmt = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        role_permission = (await db.execute(stmt)).scalar_one_or_none()
        if role_permission is None:
            raise HTTPException(status_code=404, detail="Role permission not found")

        db.delete(role_permission)
        await db.flush()

    async def get_user_permissions(
        self, user_id: uuid.UUID, db: AsyncSession
    ) -> list[Permission]:
        stmt = (
            select(User)
            .options(selectinload(User.role).selectinload(Role.permissions))
            .where(User.id == user_id)
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if user.role is None:
            return []
        return list(user.role.permissions)
