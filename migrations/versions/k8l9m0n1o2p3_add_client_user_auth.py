"""add client user auth

Revision ID: k8l9m0n1o2p3
Revises: j7k8l9m0n1o2
Create Date: 2026-05-20 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "k8l9m0n1o2p3"
down_revision: Union[str, None] = "j7k8l9m0n1o2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "client_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=True),
        sa.Column("role", sa.String(length=40), nullable=False, server_default="owner"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_client_users_id"), "client_users", ["id"], unique=False)
    op.create_index(op.f("ix_client_users_client_id"), "client_users", ["client_id"], unique=False)
    op.create_index(op.f("ix_client_users_email"), "client_users", ["email"], unique=True)

    op.create_table(
        "client_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["client_users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(op.f("ix_client_sessions_id"), "client_sessions", ["id"], unique=False)
    op.create_index(op.f("ix_client_sessions_user_id"), "client_sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_client_sessions_client_id"), "client_sessions", ["client_id"], unique=False)
    op.create_index(op.f("ix_client_sessions_token_hash"), "client_sessions", ["token_hash"], unique=True)
    op.create_index(op.f("ix_client_sessions_expires_at"), "client_sessions", ["expires_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_client_sessions_expires_at"), table_name="client_sessions")
    op.drop_index(op.f("ix_client_sessions_token_hash"), table_name="client_sessions")
    op.drop_index(op.f("ix_client_sessions_client_id"), table_name="client_sessions")
    op.drop_index(op.f("ix_client_sessions_user_id"), table_name="client_sessions")
    op.drop_index(op.f("ix_client_sessions_id"), table_name="client_sessions")
    op.drop_table("client_sessions")
    op.drop_index(op.f("ix_client_users_email"), table_name="client_users")
    op.drop_index(op.f("ix_client_users_client_id"), table_name="client_users")
    op.drop_index(op.f("ix_client_users_id"), table_name="client_users")
    op.drop_table("client_users")
