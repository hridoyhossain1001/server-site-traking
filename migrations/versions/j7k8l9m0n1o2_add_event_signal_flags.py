"""add event signal flags

Revision ID: j7k8l9m0n1o2
Revises: i6j7k8l9m0n1
Create Date: 2026-05-19 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "j7k8l9m0n1o2"
down_revision: Union[str, None] = "i6j7k8l9m0n1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("event_logs", sa.Column("has_content_ids", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("event_logs", sa.Column("has_contents", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("event_logs", sa.Column("has_value", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("event_logs", sa.Column("has_currency", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("event_logs", sa.Column("has_user_match", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("event_logs", sa.Column("has_email_phone", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("event_logs", sa.Column("has_click_id", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("event_logs", sa.Column("has_event_id", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("event_logs", sa.Column("has_utm", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("event_logs", "has_utm")
    op.drop_column("event_logs", "has_event_id")
    op.drop_column("event_logs", "has_click_id")
    op.drop_column("event_logs", "has_email_phone")
    op.drop_column("event_logs", "has_user_match")
    op.drop_column("event_logs", "has_currency")
    op.drop_column("event_logs", "has_value")
    op.drop_column("event_logs", "has_contents")
    op.drop_column("event_logs", "has_content_ids")
