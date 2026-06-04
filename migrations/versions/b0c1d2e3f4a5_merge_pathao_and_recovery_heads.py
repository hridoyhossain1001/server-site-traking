"""merge pathao and recovery heads

Revision ID: b0c1d2e3f4a5
Revises: a0b1c2d3e4f5, d4e5f6g7h8i9
Create Date: 2026-06-02 00:00:00.000000
"""

from typing import Sequence, Union


revision: str = "b0c1d2e3f4a5"
down_revision: Union[str, Sequence[str], None] = ("a0b1c2d3e4f5", "d4e5f6g7h8i9")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
