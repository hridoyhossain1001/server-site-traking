"""add public_key to clients

Revision ID: e2f3g4h5i6j7
Revises: d1e2f3g4h5i6
"""
from typing import Sequence, Union
import secrets

from alembic import op
import sqlalchemy as sa


revision: str = "e2f3g4h5i6j7"
down_revision: Union[str, None] = "d1e2f3g4h5i6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("public_key", sa.String(), nullable=True))

    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id FROM clients WHERE public_key IS NULL")).fetchall()
    used: set[str] = set()
    for row in rows:
        public_key = secrets.token_urlsafe(24)
        while public_key in used:
            public_key = secrets.token_urlsafe(24)
        used.add(public_key)
        conn.execute(
            sa.text("UPDATE clients SET public_key = :public_key WHERE id = :client_id"),
            {"public_key": public_key, "client_id": row.id},
        )

    op.alter_column("clients", "public_key", nullable=False)
    op.create_unique_constraint("uq_clients_public_key", "clients", ["public_key"])


def downgrade() -> None:
    op.drop_constraint("uq_clients_public_key", "clients", type_="unique")
    op.drop_column("clients", "public_key")
