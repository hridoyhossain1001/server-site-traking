"""add event_name index to event_logs

Revision ID: c9d0e1f2g3h4
Revises: b8c9d0e1f2g3
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9d0e1f2g3h4'
down_revision: Union[str, None] = 'b8c9d0e1f2g3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(op.f('ix_event_logs_event_name'), 'event_logs', ['event_name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_event_logs_event_name'), table_name='event_logs')
