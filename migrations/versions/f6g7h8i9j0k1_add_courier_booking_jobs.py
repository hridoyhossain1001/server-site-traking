"""add durable courier booking jobs

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2026-06-02 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6g7h8i9j0k1"
down_revision: Union[str, None] = "e5f6g7h8i9j0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "courier_booking_jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("pending_event_id", sa.Integer(), nullable=True),
        sa.Column("courier_order_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("request_payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("locked_by", sa.String(length=255), nullable=True),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["courier_order_id"], ["courier_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["pending_event_id"], ["pending_events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("courier_order_id", name="uq_courier_booking_job_order"),
    )
    op.create_index(op.f("ix_courier_booking_jobs_id"), "courier_booking_jobs", ["id"], unique=False)
    op.create_index(op.f("ix_courier_booking_jobs_client_id"), "courier_booking_jobs", ["client_id"], unique=False)
    op.create_index(op.f("ix_courier_booking_jobs_pending_event_id"), "courier_booking_jobs", ["pending_event_id"], unique=False)
    op.create_index(op.f("ix_courier_booking_jobs_courier_order_id"), "courier_booking_jobs", ["courier_order_id"], unique=False)
    op.create_index(op.f("ix_courier_booking_jobs_status"), "courier_booking_jobs", ["status"], unique=False)
    op.create_index(op.f("ix_courier_booking_jobs_next_attempt_at"), "courier_booking_jobs", ["next_attempt_at"], unique=False)
    op.create_index(op.f("ix_courier_booking_jobs_created_at"), "courier_booking_jobs", ["created_at"], unique=False)
    op.create_index(
        "ix_courier_booking_jobs_claim",
        "courier_booking_jobs",
        ["status", "next_attempt_at", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_courier_booking_jobs_client_status",
        "courier_booking_jobs",
        ["client_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_courier_booking_jobs_client_status", table_name="courier_booking_jobs")
    op.drop_index("ix_courier_booking_jobs_claim", table_name="courier_booking_jobs")
    op.drop_index(op.f("ix_courier_booking_jobs_created_at"), table_name="courier_booking_jobs")
    op.drop_index(op.f("ix_courier_booking_jobs_next_attempt_at"), table_name="courier_booking_jobs")
    op.drop_index(op.f("ix_courier_booking_jobs_status"), table_name="courier_booking_jobs")
    op.drop_index(op.f("ix_courier_booking_jobs_courier_order_id"), table_name="courier_booking_jobs")
    op.drop_index(op.f("ix_courier_booking_jobs_pending_event_id"), table_name="courier_booking_jobs")
    op.drop_index(op.f("ix_courier_booking_jobs_client_id"), table_name="courier_booking_jobs")
    op.drop_index(op.f("ix_courier_booking_jobs_id"), table_name="courier_booking_jobs")
    op.drop_table("courier_booking_jobs")
