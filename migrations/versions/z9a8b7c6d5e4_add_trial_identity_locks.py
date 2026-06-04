"""add trial identity locks

Revision ID: z9a8b7c6d5e4
Revises: y3z4a5b6c7d8
Create Date: 2026-06-01 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "z9a8b7c6d5e4"
down_revision: Union[str, None] = "y3z4a5b6c7d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "trial_identities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=True),
        sa.Column("domain", sa.String(length=255), nullable=True),
        sa.Column("pixel_id", sa.String(length=64), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="signup"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trial_identities_client_id"), "trial_identities", ["client_id"], unique=False)
    op.create_index(op.f("ix_trial_identities_domain"), "trial_identities", ["domain"], unique=True)
    op.create_index(op.f("ix_trial_identities_pixel_id"), "trial_identities", ["pixel_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_trial_identities_pixel_id"), table_name="trial_identities")
    op.drop_index(op.f("ix_trial_identities_domain"), table_name="trial_identities")
    op.drop_index(op.f("ix_trial_identities_client_id"), table_name="trial_identities")
    op.drop_table("trial_identities")
