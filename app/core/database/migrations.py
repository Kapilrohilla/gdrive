from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection


def _constraint_exists(inspector, table: str, constraint_name: str) -> bool:
    for fk in inspector.get_foreign_keys(table):
        if fk.get("name") == constraint_name:
            return True
    return False


def _column_is_nullable(inspector, table: str, column: str) -> bool:
    for col in inspector.get_columns(table):
        if col["name"] == column:
            return col.get("nullable", True)
    return True


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
