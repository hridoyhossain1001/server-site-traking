"""missing revision

Revision ID: 2346a5d9e53f
Revises: 9b1c2d3e4f56
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2346a5d9e53f'
down_revision: Union[str, None] = '9b1c2d3e4f56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
