"""add visitor key to event logs

Revision ID: l0m1n2o3p4q5
Revises: h8i9j0k1l2m3
Create Date: 2026-06-04 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "l0m1n2o3p4q5"
down_revision: Union[str, None] = "h8i9j0k1l2m3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("event_logs", sa.Column("visitor_key", sa.String(length=80), nullable=True))
    op.create_index(op.f("ix_event_logs_visitor_key"), "event_logs", ["visitor_key"], unique=False)
    op.create_index(
        "ix_event_logs_visitor_funnel",
        "event_logs",
        ["client_id", "geo_district", "event_name", "visitor_key", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_event_logs_visitor_funnel", table_name="event_logs")
    op.drop_index(op.f("ix_event_logs_visitor_key"), table_name="event_logs")
    op.drop_column("event_logs", "visitor_key")
