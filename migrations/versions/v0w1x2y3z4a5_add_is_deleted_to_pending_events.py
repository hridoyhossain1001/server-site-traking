"""add is_deleted to pending_events

Revision ID: v0w1x2y3z4a5
Revises: u9v0w1x2y3z4
Create Date: 2026-05-29 22:50:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "v0w1x2y3z4a5"
down_revision: Union[str, None] = "u9v0w1x2y3z4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        existing = {row[1] for row in bind.exec_driver_sql("PRAGMA table_info(pending_events)").fetchall()}
        if "is_deleted" not in existing:
            op.add_column("pending_events", sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")))
        return

    op.execute("ALTER TABLE pending_events ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT false")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return
    op.execute("ALTER TABLE pending_events DROP COLUMN IF EXISTS is_deleted")
