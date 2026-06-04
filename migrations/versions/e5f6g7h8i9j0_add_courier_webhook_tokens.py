"""add per-client SteadFast and RedX webhook tokens

Revision ID: e5f6g7h8i9j0
Revises: b0c1d2e3f4a5
Create Date: 2026-06-02 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5f6g7h8i9j0"
down_revision: Union[str, None] = "b0c1d2e3f4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("steadfast_webhook_token", sa.String(), nullable=True))
    op.add_column("clients", sa.Column("redx_webhook_secret", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("clients", "redx_webhook_secret")
    op.drop_column("clients", "steadfast_webhook_token")
