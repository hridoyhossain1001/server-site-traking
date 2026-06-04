"""add plugin connect sessions

Revision ID: i8j9k0l1m2n3
Revises: h8i9j0k1l2m3
Create Date: 2026-06-03 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "i8j9k0l1m2n3"
down_revision: Union[str, None] = "h8i9j0k1l2m3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "plugin_connect_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("site_url", sa.String(length=512), nullable=False),
        sa.Column("site_host", sa.String(length=255), nullable=False),
        sa.Column("return_url", sa.String(length=1024), nullable=False),
        sa.Column("state", sa.String(length=128), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("code_challenge", sa.String(length=96), nullable=False),
        sa.Column("created_ip", sa.String(length=64), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plugin_connect_sessions_id"), "plugin_connect_sessions", ["id"], unique=False)
    op.create_index(op.f("ix_plugin_connect_sessions_client_id"), "plugin_connect_sessions", ["client_id"], unique=False)
    op.create_index(op.f("ix_plugin_connect_sessions_site_host"), "plugin_connect_sessions", ["site_host"], unique=False)
    op.create_index(op.f("ix_plugin_connect_sessions_code_hash"), "plugin_connect_sessions", ["code_hash"], unique=True)
    op.create_index(op.f("ix_plugin_connect_sessions_expires_at"), "plugin_connect_sessions", ["expires_at"], unique=False)
    op.create_index(op.f("ix_plugin_connect_sessions_used_at"), "plugin_connect_sessions", ["used_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_plugin_connect_sessions_used_at"), table_name="plugin_connect_sessions")
    op.drop_index(op.f("ix_plugin_connect_sessions_expires_at"), table_name="plugin_connect_sessions")
    op.drop_index(op.f("ix_plugin_connect_sessions_code_hash"), table_name="plugin_connect_sessions")
    op.drop_index(op.f("ix_plugin_connect_sessions_site_host"), table_name="plugin_connect_sessions")
    op.drop_index(op.f("ix_plugin_connect_sessions_client_id"), table_name="plugin_connect_sessions")
    op.drop_index(op.f("ix_plugin_connect_sessions_id"), table_name="plugin_connect_sessions")
    op.drop_table("plugin_connect_sessions")
