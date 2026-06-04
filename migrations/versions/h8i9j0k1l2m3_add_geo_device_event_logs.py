"""add geo and device fields to event logs

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-06-03 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "h8i9j0k1l2m3"
down_revision: Union[str, None] = "g7h8i9j0k1l2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("event_logs", sa.Column("geo_country", sa.String(length=8), nullable=True))
    op.add_column("event_logs", sa.Column("geo_region", sa.String(length=80), nullable=True))
    op.add_column("event_logs", sa.Column("geo_city", sa.String(length=80), nullable=True))
    op.add_column("event_logs", sa.Column("geo_district", sa.String(length=80), nullable=True))
    op.add_column("event_logs", sa.Column("device_type", sa.String(length=24), nullable=True))
    op.add_column("event_logs", sa.Column("device_os", sa.String(length=40), nullable=True))
    op.add_column("event_logs", sa.Column("device_browser", sa.String(length=40), nullable=True))
    op.add_column("event_logs", sa.Column("screen_width", sa.Integer(), nullable=True))
    op.add_column("event_logs", sa.Column("screen_height", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_event_logs_geo_country"), "event_logs", ["geo_country"], unique=False)
    op.create_index("ix_event_logs_geo_district", "event_logs", ["client_id", "geo_district", "created_at"], unique=False)
    op.create_index("ix_event_logs_device_type", "event_logs", ["client_id", "device_type", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_event_logs_device_type", table_name="event_logs")
    op.drop_index("ix_event_logs_geo_district", table_name="event_logs")
    op.drop_index(op.f("ix_event_logs_geo_country"), table_name="event_logs")
    op.drop_column("event_logs", "screen_height")
    op.drop_column("event_logs", "screen_width")
    op.drop_column("event_logs", "device_browser")
    op.drop_column("event_logs", "device_os")
    op.drop_column("event_logs", "device_type")
    op.drop_column("event_logs", "geo_district")
    op.drop_column("event_logs", "geo_city")
    op.drop_column("event_logs", "geo_region")
    op.drop_column("event_logs", "geo_country")
