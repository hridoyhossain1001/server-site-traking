"""add event dedup and retry claim index

Revision ID: 9b1c2d3e4f56
Revises: f125ee6894bf
Create Date: 2026-05-05 19:10:00.000000
"""
from typing import Sequence, Union

from alembic import op


revision: str = "9b1c2d3e4f56"
down_revision: Union[str, None] = "f125ee6894bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS event_deduplications (
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES clients(id),
            event_id VARCHAR NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_event_deduplications_client_event_id
        ON event_deduplications (client_id, event_id)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_event_deduplications_client_id
        ON event_deduplications (client_id)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_event_deduplications_created_at
        ON event_deduplications (created_at)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_failed_events_retry_claim
        ON failed_events (status, retry_count, created_at)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_failed_events_retry_claim")
    op.execute("DROP INDEX IF EXISTS ix_event_deduplications_created_at")
    op.execute("DROP INDEX IF EXISTS ix_event_deduplications_client_id")
    op.execute("DROP INDEX IF EXISTS uq_event_deduplications_client_event_id")
    op.execute("DROP TABLE IF EXISTS event_deduplications")
