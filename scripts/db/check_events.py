import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.client import Client
from app.models.event_log import EventLog

async def run():
    async with AsyncSessionLocal() as db:
        # Find client
        res = await db.execute(select(Client).where(Client.domain == "metroomaa.com"))
        client = res.scalar()
        if not client:
            res = await db.execute(select(Client).where(Client.name.ilike("%metroomaa.com%")))
            client = res.scalar()

        if not client:
            print("Client metroomaa.com not found in local DB.")
            return

        print(f"Found client: {client.name} (ID: {client.id}, Domain: {client.domain})")

        # Get recent events
        res = await db.execute(
            select(EventLog.event_name, EventLog.status, EventLog.created_at)
            .where(EventLog.client_id == client.id)
            .order_by(EventLog.created_at.desc())
            .limit(20)
        )
        events = res.all()

        if not events:
            print("No recent events found.")
        else:
            print("Recent events:")
            for e in events:
                print(f"- {e.created_at}: {e.event_name} ({e.status})")

if __name__ == "__main__":
    asyncio.run(run())
