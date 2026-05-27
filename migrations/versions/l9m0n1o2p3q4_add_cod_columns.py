"""add cod columns

Revision ID: l9m0n1o2p3q4
Revises: k8l9m0n1o2p3
Create Date: 2026-05-24 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "l9m0n1o2p3q4"
down_revision: Union[str, None] = "k8l9m0n1o2p3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to clients table
    op.add_column(
        "clients",
        sa.Column("auto_confirm_days", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "clients",
        sa.Column("auto_confirm_status", sa.String(length=255), nullable=True, server_default="completed")
    )


def downgrade() -> None:
    op.drop_column("clients", "auto_confirm_status")
    op.drop_column("clients", "auto_confirm_days")
