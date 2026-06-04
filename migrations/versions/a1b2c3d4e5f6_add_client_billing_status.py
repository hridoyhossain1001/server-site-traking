"""add client billing status

Revision ID: a1b2c3d4e5f6
Revises: z9a8b7c6d5e4
Create Date: 2026-06-01 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "z9a8b7c6d5e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "clients",
        sa.Column("billing_status", sa.String(), nullable=False, server_default="paid"),
    )


def downgrade() -> None:
    op.drop_column("clients", "billing_status")
