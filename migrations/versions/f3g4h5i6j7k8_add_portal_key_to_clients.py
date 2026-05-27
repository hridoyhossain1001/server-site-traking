"""add portal_key to clients

Revision ID: f3g4h5i6j7k8
Revises: e2f3g4h5i6j7
"""
from typing import Sequence, Union
import secrets

from alembic import op
import sqlalchemy as sa


revision: str = "f3g4h5i6j7k8"
down_revision: Union[str, None] = "e2f3g4h5i6j7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("portal_key", sa.String(), nullable=True))

    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id FROM clients WHERE portal_key IS NULL")).fetchall()
    used: set[str] = set()
    for row in rows:
        portal_key = secrets.token_urlsafe(24)
        while portal_key in used:
            portal_key = secrets.token_urlsafe(24)
        used.add(portal_key)
        conn.execute(
            sa.text("UPDATE clients SET portal_key = :portal_key WHERE id = :client_id"),
            {"portal_key": portal_key, "client_id": row.id},
        )

    op.create_unique_constraint("uq_clients_portal_key", "clients", ["portal_key"])


def downgrade() -> None:
    op.drop_constraint("uq_clients_portal_key", "clients", type_="unique")
    op.drop_column("clients", "portal_key")
