"""add client plan trials

Revision ID: y3z4a5b6c7d8
Revises: x2y3z4a5b6c7
Create Date: 2026-06-01 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "y3z4a5b6c7d8"
down_revision: Union[str, None] = "x2y3z4a5b6c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PLAN_COLUMNS = (
    ("plan_tier", sa.String(), False, sa.text("'growth'")),
    ("trial_started_at", sa.DateTime(timezone=True), True, None),
    ("trial_ends_at", sa.DateTime(timezone=True), True, None),
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        existing = {row[1] for row in bind.exec_driver_sql("PRAGMA table_info(clients)").fetchall()}
        for name, column_type, nullable, server_default in PLAN_COLUMNS:
            if name not in existing:
                op.add_column(
                    "clients",
                    sa.Column(name, column_type, nullable=nullable, server_default=server_default),
                )
        return

    op.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS plan_tier VARCHAR NOT NULL DEFAULT 'growth'")
    op.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS trial_started_at TIMESTAMPTZ")
    op.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS trial_ends_at TIMESTAMPTZ")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return
    op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS trial_ends_at")
    op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS trial_started_at")
    op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS plan_tier")
