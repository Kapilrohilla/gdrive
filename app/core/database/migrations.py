from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection

from app.constants.permissions import (
    MEMBER_PERMISSION_NAMES,
    PERMISSION_DEFINITIONS,
    STANDARD_ROLE_ADMIN,
    STANDARD_ROLE_MEMBER,
    permission_name,
)


def _constraint_exists(inspector, table: str, constraint_name: str) -> bool:
    for fk in inspector.get_foreign_keys(table):
        if fk.get("name") == constraint_name:
            return True
    return False


def _column_exists(inspector, table: str, column: str) -> bool:
    return column in {col["name"] for col in inspector.get_columns(table)}


def _column_is_nullable(inspector, table: str, column: str) -> bool:
    for col in inspector.get_columns(table):
        if col["name"] == column:
            return col.get("nullable", True)
    return True


def _seed_standard_rbac(connection: Connection) -> None:
    inspector = inspect(connection)
    if not _column_exists(inspector, "roles", "is_standard"):
        connection.execute(
            text(
                "ALTER TABLE roles ADD COLUMN is_standard BOOLEAN NOT NULL DEFAULT FALSE"
            )
        )

    for resource, action, description in PERMISSION_DEFINITIONS:
        name = permission_name(resource, action)
        connection.execute(
            text(
                """
                INSERT INTO permissions (id, name, resource, action, description, created_at, updated_at)
                SELECT gen_random_uuid(), :name, :resource, :action, :description, NOW(), NOW()
                WHERE NOT EXISTS (SELECT 1 FROM permissions WHERE name = :name)
                """
            ),
            {
                "name": name,
                "resource": resource,
                "action": action.value,
                "description": description,
            },
        )

    for role_name, description in (
        (STANDARD_ROLE_ADMIN, "Full system access with all permissions"),
        (STANDARD_ROLE_MEMBER, "Standard member access to own files, folders, and short URLs"),
    ):
        connection.execute(
            text(
                """
                INSERT INTO roles (id, name, description, is_system, is_standard, created_at, updated_at)
                SELECT gen_random_uuid(), :name, :description, TRUE, TRUE, NOW(), NOW()
                WHERE NOT EXISTS (SELECT 1 FROM roles WHERE name = :name)
                """
            ),
            {"name": role_name, "description": description},
        )
        connection.execute(
            text(
                """
                UPDATE roles
                SET is_system = TRUE, is_standard = TRUE, description = :description
                WHERE name = :name
                """
            ),
            {"name": role_name, "description": description},
        )

    connection.execute(
        text(
            """
            INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at)
            SELECT gen_random_uuid(), r.id, p.id, NOW(), NOW()
            FROM roles r
            CROSS JOIN permissions p
            WHERE r.name = :admin_role
            AND NOT EXISTS (
                SELECT 1 FROM role_permissions rp
                WHERE rp.role_id = r.id AND rp.permission_id = p.id
            )
            """
        ),
        {"admin_role": STANDARD_ROLE_ADMIN},
    )

    for permission_name_value in MEMBER_PERMISSION_NAMES:
        connection.execute(
            text(
                """
                INSERT INTO role_permissions (id, role_id, permission_id, created_at, updated_at)
                SELECT gen_random_uuid(), r.id, p.id, NOW(), NOW()
                FROM roles r
                JOIN permissions p ON p.name = :permission_name
                WHERE r.name = :member_role
                AND NOT EXISTS (
                    SELECT 1 FROM role_permissions rp
                    WHERE rp.role_id = r.id AND rp.permission_id = p.id
                )
                """
            ),
            {
                "member_role": STANDARD_ROLE_MEMBER,
                "permission_name": permission_name_value,
            },
        )


def apply_schema_migrations(connection: Connection) -> None:
    inspector = inspect(connection)
    session_columns = {column["name"] for column in inspector.get_columns("sessions")}
    visitor_columns = {column["name"] for column in inspector.get_columns("visitors")}

    needs_visitor_migration = "visitor_id" not in session_columns
    if needs_visitor_migration:
        connection.execute(text("ALTER TABLE sessions ADD COLUMN visitor_id UUID"))

    inspector = inspect(connection)
    visitor_id_nullable = _column_is_nullable(inspector, "sessions", "visitor_id")

    if needs_visitor_migration or visitor_id_nullable:
        connection.execute(
            text(
                "DELETE FROM auth_events WHERE session_id IN "
                "(SELECT id FROM sessions WHERE visitor_id IS NULL)"
            )
        )
        connection.execute(text("DELETE FROM sessions WHERE visitor_id IS NULL"))

        if not _constraint_exists(inspector, "sessions", "sessions_visitor_id_fkey"):
            connection.execute(
                text(
                    "ALTER TABLE sessions ADD CONSTRAINT sessions_visitor_id_fkey "
                    "FOREIGN KEY (visitor_id) REFERENCES visitors(id)"
                )
            )

        connection.execute(text("ALTER TABLE sessions ALTER COLUMN visitor_id SET NOT NULL"))

    if "user_id" in visitor_columns:
        connection.execute(text("ALTER TABLE visitors DROP COLUMN user_id"))

    inspector = inspect(connection)
    if "roles" in inspector.get_table_names():
        _seed_standard_rbac(connection)
