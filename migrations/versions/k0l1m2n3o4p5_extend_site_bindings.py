"""extend site bindings

Revision ID: k0l1m2n3o4p5
Revises: j9k0l1m2n3o4
Create Date: 2026-06-03 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "k0l1m2n3o4p5"
down_revision: Union[str, None] = "j9k0l1m2n3o4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("site_bindings", sa.Column("installation_id", sa.String(length=128), nullable=True))
    op.add_column("site_bindings", sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("site_bindings", sa.Column("released_by", sa.String(length=128), nullable=True))
    op.add_column("site_bindings", sa.Column("release_reason", sa.Text(), nullable=True))
    op.create_index(op.f("ix_site_bindings_installation_id"), "site_bindings", ["installation_id"], unique=False)
    op.create_index(op.f("ix_site_bindings_last_event_at"), "site_bindings", ["last_event_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_site_bindings_last_event_at"), table_name="site_bindings")
    op.drop_index(op.f("ix_site_bindings_installation_id"), table_name="site_bindings")
    op.drop_column("site_bindings", "release_reason")
    op.drop_column("site_bindings", "released_by")
    op.drop_column("site_bindings", "last_event_at")
    op.drop_column("site_bindings", "installation_id")
