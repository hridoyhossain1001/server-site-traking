"""add client phone and support notes

Revision ID: g7h8i9j0k1l2
Revises: f6g7h8i9j0k1
Create Date: 2026-06-03 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, None] = "f6g7h8i9j0k1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("client_users", sa.Column("phone_number", sa.String(length=32), nullable=True))
    op.create_index(op.f("ix_client_users_phone_number"), "client_users", ["phone_number"], unique=False)
    op.create_table(
        "client_support_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_client_support_notes_id"), "client_support_notes", ["id"], unique=False)
    op.create_index(op.f("ix_client_support_notes_client_id"), "client_support_notes", ["client_id"], unique=False)
    op.create_index(op.f("ix_client_support_notes_created_at"), "client_support_notes", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_client_support_notes_created_at"), table_name="client_support_notes")
    op.drop_index(op.f("ix_client_support_notes_client_id"), table_name="client_support_notes")
    op.drop_index(op.f("ix_client_support_notes_id"), table_name="client_support_notes")
    op.drop_table("client_support_notes")
    op.drop_index(op.f("ix_client_users_phone_number"), table_name="client_users")
    op.drop_column("client_users", "phone_number")
