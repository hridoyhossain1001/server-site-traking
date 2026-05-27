"""Add composite index to EventLog

Revision ID: 6f95f5ca1ac2
Revises: 9b1c2d3e4f56
Create Date: 2026-05-16 00:43:49.974537
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f95f5ca1ac2'
down_revision: Union[str, None] = '2346a5d9e53f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_event_logs_analytics', 'event_logs', ['client_id', 'event_name', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_event_logs_analytics', table_name='event_logs')
