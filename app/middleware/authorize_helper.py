from collections.abc import Iterable
from uuid import UUID

from fastapi import HTTPException, Request

from app.api.deps import DbSession
from app.constants.permissions import permission_name
from app.models.iam.permission import PermissionAction
from app.services.iam.rbac import RbacService

rbac_service = RbacService()


def require_permissions(
    permissions: Iterable[str],
    *,
    require_all: bool = True,
):
    """
    Creates a dependency that checks whether the authenticated user
    has the required permissions.

    Must be used together with authenticate(TokenType.ACCESS), which sets
    request.state.user_id.

    Args:
        permissions: Required permission names (matches Permission.name).
        require_all: If True, user must have all permissions.
                     If False, user must have at least one.
    """
    required_permissions = {permission.strip() for permission in permissions if permission.strip()}

    if not required_permissions:
        raise ValueError("At least one permission is required")

    async def dependency(request: Request, db: DbSession) -> None:
        user_id = getattr(request.state, "user_id", None)
        if user_id is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        user_permissions = await rbac_service.get_user_permissions(
            UUID(str(user_id)),
            db,
        )
        granted_permissions = {permission.name for permission in user_permissions}

        if require_all:
            has_permission = required_permissions.issubset(granted_permissions)
        else:
            has_permission = bool(required_permissions.intersection(granted_permissions))

        if not has_permission:
            raise HTTPException(status_code=403, detail="Forbidden")

    return dependency


def require_permission(resource: str, action: PermissionAction | str):
    """Require a single permission built from resource and action."""
    return require_permissions([permission_name(resource, action)])
