"""add incomplete checkout recovery

Revision ID: a0b1c2d3e4f5
Revises: z9a8b7c6d5e4
Create Date: 2026-06-02 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a0b1c2d3e4f5"
down_revision: Union[str, None] = "z9a8b7c6d5e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "incomplete_checkouts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("visitor_id", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("phone_hash", sa.String(length=64), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("products", sa.JSON(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(length=8), nullable=False, server_default="BDT"),
        sa.Column("page_url", sa.String(length=1000), nullable=True),
        sa.Column("campaign_data", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("order_id", sa.String(length=255), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_incomplete_checkouts_client_id", "incomplete_checkouts", ["client_id"], unique=False)
    op.create_index("ix_incomplete_checkouts_id", "incomplete_checkouts", ["id"], unique=False)
    op.create_index("ix_incomplete_checkouts_order_id", "incomplete_checkouts", ["order_id"], unique=False)
    op.create_index("ix_incomplete_checkouts_status", "incomplete_checkouts", ["status"], unique=False)
    op.create_index("ix_incomplete_client_status_activity", "incomplete_checkouts", ["client_id", "status", "last_activity_at"], unique=False)
    op.create_index("ix_incomplete_client_visitor_phone", "incomplete_checkouts", ["client_id", "visitor_id", "phone_hash"], unique=False)


def downgrade() -> None:
    op.drop_table("incomplete_checkouts")
