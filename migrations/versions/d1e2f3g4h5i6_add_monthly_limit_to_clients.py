"""add monthly_limit to clients

Revision ID: d1e2f3g4h5i6
Revises: c9d0e1f2g3h4
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1e2f3g4h5i6'
down_revision: Union[str, None] = 'c9d0e1f2g3h4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('clients', sa.Column('monthly_limit', sa.Integer(), nullable=True, server_default='50000'))


def downgrade() -> None:
    op.drop_column('clients', 'monthly_limit')
