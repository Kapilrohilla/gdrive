from app.models.iam.permission import PermissionAction


def permission_name(resource: str, action: PermissionAction | str) -> str:
    action_value = action.value if isinstance(action, PermissionAction) else action
    return f"{resource}.{action_value}"


STANDARD_ROLE_ADMIN = "Admin"
STANDARD_ROLE_MEMBER = "Member"

PERMISSION_DEFINITIONS: list[tuple[str, PermissionAction, str]] = [
    ("files", PermissionAction.READ, "List files and view file metadata"),
    ("files", PermissionAction.SELECT, "Download and preview files"),
    ("files", PermissionAction.CREATE, "Generate file upload links"),
    ("files", PermissionAction.UPDATE, "Mark file uploads complete"),
    ("files", PermissionAction.DELETE, "Delete files"),
    ("folders", PermissionAction.READ, "List own folders"),
    ("folders", PermissionAction.CREATE, "Create folders"),
    ("folders", PermissionAction.UPDATE, "Update folders"),
    ("folders", PermissionAction.DELETE, "Delete folders"),
    ("file_activity", PermissionAction.READ, "View activity for a file"),
    ("my_file_activity", PermissionAction.READ, "View activity across own files"),
    ("short_urls", PermissionAction.CREATE, "Create short URLs"),
    ("short_urls", PermissionAction.READ, "List own short URLs"),
    ("short_urls", PermissionAction.MANAGE, "Manage all short URLs"),
    ("users", PermissionAction.READ, "List users"),
    ("users", PermissionAction.CREATE, "Create users"),
    ("visitors", PermissionAction.READ, "List visitors"),
    ("auth_events", PermissionAction.READ, "List auth events"),
    ("roles", PermissionAction.READ, "List roles"),
    ("roles", PermissionAction.CREATE, "Create roles"),
    ("roles", PermissionAction.UPDATE, "Update roles"),
    ("roles", PermissionAction.DELETE, "Delete roles"),
    ("permissions", PermissionAction.READ, "List permissions"),
    ("permissions", PermissionAction.CREATE, "Create permissions"),
    ("permissions", PermissionAction.UPDATE, "Update permissions"),
    ("permissions", PermissionAction.DELETE, "Delete permissions"),
]

MEMBER_PERMISSION_NAMES: set[str] = {
    permission_name(resource, action)
    for resource, action in [
        ("files", PermissionAction.READ),
        ("files", PermissionAction.CREATE),
        ("files", PermissionAction.UPDATE),
        ("folders", PermissionAction.READ),
        ("folders", PermissionAction.CREATE),
        ("file_activity", PermissionAction.READ),
        ("my_file_activity", PermissionAction.READ),
        ("short_urls", PermissionAction.CREATE),
        ("short_urls", PermissionAction.READ),
    ]
}

ALL_PERMISSION_NAMES: set[str] = {
    permission_name(resource, action) for resource, action, _ in PERMISSION_DEFINITIONS
}
