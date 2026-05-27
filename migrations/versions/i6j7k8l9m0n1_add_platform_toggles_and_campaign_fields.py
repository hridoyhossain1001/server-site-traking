"""add platform toggles and campaign fields

Revision ID: i6j7k8l9m0n1
Revises: h5i6j7k8l9m0
Create Date: 2026-05-19
"""

from alembic import op
import sqlalchemy as sa


revision = "i6j7k8l9m0n1"
down_revision = "h5i6j7k8l9m0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("enable_facebook", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("clients", sa.Column("enable_tiktok", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("clients", sa.Column("enable_ga4", sa.Boolean(), nullable=False, server_default=sa.true()))

    op.add_column("event_logs", sa.Column("value", sa.Float(), nullable=True))
    op.add_column("event_logs", sa.Column("currency", sa.String(), nullable=True))
    op.add_column("event_logs", sa.Column("campaign_source", sa.String(), nullable=True))
    op.add_column("event_logs", sa.Column("utm_source", sa.String(), nullable=True))
    op.add_column("event_logs", sa.Column("utm_medium", sa.String(), nullable=True))
    op.add_column("event_logs", sa.Column("utm_campaign", sa.String(), nullable=True))
    op.add_column("event_logs", sa.Column("utm_content", sa.String(), nullable=True))
    op.add_column("event_logs", sa.Column("utm_term", sa.String(), nullable=True))
    op.create_index("ix_event_logs_campaign_source", "event_logs", ["campaign_source"])
    op.create_index("ix_event_logs_utm_source", "event_logs", ["utm_source"])
    op.create_index("ix_event_logs_utm_campaign", "event_logs", ["utm_campaign"])
    op.create_index("ix_event_logs_campaign", "event_logs", ["client_id", "utm_source", "utm_campaign", "created_at"])

    op.alter_column("clients", "enable_facebook", server_default=None)
    op.alter_column("clients", "enable_tiktok", server_default=None)
    op.alter_column("clients", "enable_ga4", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_event_logs_campaign", table_name="event_logs")
    op.drop_index("ix_event_logs_utm_campaign", table_name="event_logs")
    op.drop_index("ix_event_logs_utm_source", table_name="event_logs")
    op.drop_index("ix_event_logs_campaign_source", table_name="event_logs")
    op.drop_column("event_logs", "utm_term")
    op.drop_column("event_logs", "utm_content")
    op.drop_column("event_logs", "utm_campaign")
    op.drop_column("event_logs", "utm_medium")
    op.drop_column("event_logs", "utm_source")
    op.drop_column("event_logs", "campaign_source")
    op.drop_column("event_logs", "currency")
    op.drop_column("event_logs", "value")
    op.drop_column("clients", "enable_ga4")
    op.drop_column("clients", "enable_tiktok")
    op.drop_column("clients", "enable_facebook")
