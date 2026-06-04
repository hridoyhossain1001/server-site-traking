"""add site bindings

Revision ID: j9k0l1m2n3o4
Revises: i8j9k0l1m2n3
Create Date: 2026-06-03 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "j9k0l1m2n3o4"
down_revision: Union[str, None] = "i8j9k0l1m2n3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "site_bindings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("site_host", sa.String(length=255), nullable=False),
        sa.Column("root_domain", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="plugin_connect"),
        sa.Column("connected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_site_bindings_id"), "site_bindings", ["id"], unique=False)
    op.create_index(op.f("ix_site_bindings_client_id"), "site_bindings", ["client_id"], unique=False)
    op.create_index(op.f("ix_site_bindings_site_host"), "site_bindings", ["site_host"], unique=False)
    op.create_index(op.f("ix_site_bindings_root_domain"), "site_bindings", ["root_domain"], unique=False)
    op.create_index(op.f("ix_site_bindings_status"), "site_bindings", ["status"], unique=False)
    op.create_index(op.f("ix_site_bindings_released_at"), "site_bindings", ["released_at"], unique=False)
    op.create_index("ix_site_bindings_root_status", "site_bindings", ["root_domain", "status"], unique=False)
    op.create_index("ix_site_bindings_site_status", "site_bindings", ["site_host", "status"], unique=False)
    op.create_index("ix_site_bindings_client_status", "site_bindings", ["client_id", "status"], unique=False)
    op.create_index(
        "uq_site_bindings_active_root_domain",
        "site_bindings",
        ["root_domain"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    op.drop_index("uq_site_bindings_active_root_domain", table_name="site_bindings")
    op.drop_index("ix_site_bindings_client_status", table_name="site_bindings")
    op.drop_index("ix_site_bindings_site_status", table_name="site_bindings")
    op.drop_index("ix_site_bindings_root_status", table_name="site_bindings")
    op.drop_index(op.f("ix_site_bindings_released_at"), table_name="site_bindings")
    op.drop_index(op.f("ix_site_bindings_status"), table_name="site_bindings")
    op.drop_index(op.f("ix_site_bindings_root_domain"), table_name="site_bindings")
    op.drop_index(op.f("ix_site_bindings_site_host"), table_name="site_bindings")
    op.drop_index(op.f("ix_site_bindings_client_id"), table_name="site_bindings")
    op.drop_index(op.f("ix_site_bindings_id"), table_name="site_bindings")
    op.drop_table("site_bindings")
