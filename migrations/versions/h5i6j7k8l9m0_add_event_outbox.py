"""add event outbox

Revision ID: h5i6j7k8l9m0
Revises: g4h5i6j7k8l9
Create Date: 2026-05-18
"""

from alembic import op
import sqlalchemy as sa


revision = "h5i6j7k8l9m0"
down_revision = "g4h5i6j7k8l9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_outbox",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("event_payload", sa.JSON(), nullable=False),
        sa.Column("request_context", sa.JSON(), nullable=True),
        sa.Column("usage_reserved", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_by", sa.String(), nullable=True),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_event_outbox_id"), "event_outbox", ["id"], unique=False)
    op.create_index(op.f("ix_event_outbox_client_id"), "event_outbox", ["client_id"], unique=False)
    op.create_index(op.f("ix_event_outbox_next_attempt_at"), "event_outbox", ["next_attempt_at"], unique=False)
    op.create_index(op.f("ix_event_outbox_status"), "event_outbox", ["status"], unique=False)
    op.create_index(
        "ix_event_outbox_claim",
        "event_outbox",
        ["status", "next_attempt_at", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_event_outbox_client_status",
        "event_outbox",
        ["client_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_event_outbox_client_status", table_name="event_outbox")
    op.drop_index("ix_event_outbox_claim", table_name="event_outbox")
    op.drop_index(op.f("ix_event_outbox_status"), table_name="event_outbox")
    op.drop_index(op.f("ix_event_outbox_next_attempt_at"), table_name="event_outbox")
    op.drop_index(op.f("ix_event_outbox_client_id"), table_name="event_outbox")
    op.drop_index(op.f("ix_event_outbox_id"), table_name="event_outbox")
    op.drop_table("event_outbox")
