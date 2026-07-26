from app.models.iam.permission import PermissionAction


def permission_name(resource: str, action: PermissionAction | str) -> str:
    action_value = action.value if isinstance(action, PermissionAction) else action
    return f"{resource}.{action_value}"
