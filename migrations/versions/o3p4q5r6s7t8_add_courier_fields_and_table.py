"""add courier fields and table

Revision ID: o3p4q5r6s7t8
Revises: n2o3p4q5r6s7
Create Date: 2026-05-25 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "o3p4q5r6s7t8"
down_revision: Union[str, None] = "n2o3p4q5r6s7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _sqlite_has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    rows = bind.exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
    return any(row[1] == column_name for row in rows)


def _add_column_if_missing(table_name: str, column_name: str, ddl: str) -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        if not _sqlite_has_column(table_name, column_name):
            op.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {ddl}")
        return
    op.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {ddl}")


def upgrade() -> None:
    # 1. Add courier columns to clients table
    _add_column_if_missing("clients", "pathao_api_key", "VARCHAR(255)")
    _add_column_if_missing("clients", "pathao_secret_key", "VARCHAR(255)")
    _add_column_if_missing("clients", "pathao_store_id", "VARCHAR(255)")
    _add_column_if_missing("clients", "steadfast_api_key", "VARCHAR(255)")
    _add_column_if_missing("clients", "steadfast_secret_key", "VARCHAR(255)")
    _add_column_if_missing("clients", "courier_auto_send", "BOOLEAN DEFAULT FALSE")
    _add_column_if_missing("clients", "default_courier", "VARCHAR(50)")

    # 2. Create courier_orders table if not exists
    bind = op.get_bind()
    # For postgres:
    if bind.dialect.name == "postgresql":
        op.execute("""
        CREATE TABLE IF NOT EXISTS courier_orders (
            id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
            pending_event_id INTEGER REFERENCES pending_events(id) ON DELETE SET NULL,
            order_id VARCHAR(255) NOT NULL,
            courier_provider VARCHAR(50) NOT NULL,
            courier_order_id VARCHAR(255),
            courier_tracking_id VARCHAR(255),
            courier_status VARCHAR(100) DEFAULT 'pending',
            recipient_name VARCHAR(255),
            recipient_phone VARCHAR(50),
            recipient_address TEXT,
            cod_amount FLOAT DEFAULT 0.0,
            delivery_charge FLOAT DEFAULT 0.0,
            status_history JSONB,
            purchase_event_sent BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            delivered_at TIMESTAMP,
            UNIQUE(client_id, order_id)
        );
        """)
    else: # sqlite or other (for tests)
        op.execute("""
        CREATE TABLE IF NOT EXISTS courier_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
            pending_event_id INTEGER REFERENCES pending_events(id) ON DELETE SET NULL,
            order_id VARCHAR(255) NOT NULL,
            courier_provider VARCHAR(50) NOT NULL,
            courier_order_id VARCHAR(255),
            courier_tracking_id VARCHAR(255),
            courier_status VARCHAR(100) DEFAULT 'pending',
            recipient_name VARCHAR(255),
            recipient_phone VARCHAR(50),
            recipient_address TEXT,
            cod_amount REAL DEFAULT 0.0,
            delivery_charge REAL DEFAULT 0.0,
            status_history TEXT,
            purchase_event_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            delivered_at TIMESTAMP,
            UNIQUE(client_id, order_id)
        );
        """)


def downgrade() -> None:
    bind = op.get_bind()
    op.execute("DROP TABLE IF EXISTS courier_orders")
    if bind.dialect.name != "sqlite":
        op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS default_courier")
        op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS courier_auto_send")
        op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS steadfast_secret_key")
        op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS steadfast_api_key")
        op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS pathao_store_id")
        op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS pathao_secret_key")
        op.execute("ALTER TABLE clients DROP COLUMN IF EXISTS pathao_api_key")
