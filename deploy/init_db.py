import asyncio
import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import engine, Base

# Import all models to ensure they are registered in metadata
from app.models.client import Client
from app.models.client_user import ClientUser
from app.models.client_session import ClientSession
from app.models.event_log import EventLog
from app.models.event_outbox import EventOutbox
from app.models.failed_event import FailedEvent
from app.models.pending_event import PendingEvent
from app.models.event_dedup import EventDedup
from app.models.audit_log import AuditLog
from app.models.usage_counter import UsageCounter
from app.models.courier_order import CourierOrder

async def main():
    print("Creating all tables in PostgreSQL database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(main())
