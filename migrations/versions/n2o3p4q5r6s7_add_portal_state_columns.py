"""add portal state columns

Revision ID: n2o3p4q5r6s7
Revises: m1n2o3p4q5r6
Create Date: 2026-05-25 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op


revision: str = "n2o3p4q5r6s7"
down_revision: Union[str, None] = "m1n2o3p4q5r6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _sqlite_has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    rows = bind.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
    return any(row[1] == column_name for row in rows)


def _add_column_if_missing(table_name: str, column_name: str, ddl: str) -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        if not _sqlite_has_column(table_name, column_name):
            op.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}")
        return
    op.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {ddl}")


def upgrade() -> None:
    _add_column_if_missing("clients", "event_rules", "JSONB")
    _add_column_if_missing("clients", "resolved_suggestions", "JSONB")
    _add_column_if_missing("clients", "dismissed_suggestions", "JSONB")
    _add_column_if_missing("client_users", "notification_email", "VARCHAR(255)")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return
    op.execute("ALTER TABLE client_users DROP COLUMN IF EXISTS notification_email")
    op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS dismissed_suggestions")
    op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS resolved_suggestions")
    op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS event_rules")
