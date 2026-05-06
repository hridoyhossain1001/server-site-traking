import asyncio
from app.database import AsyncSessionLocal
from app.models.event_log import EventLog
from sqlalchemy import select, desc

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(EventLog).order_by(desc(EventLog.created_at)).limit(5))
        logs = res.scalars().all()
        print("--- LATEST EVENTS ---")
        for l in logs:
            print(f"{l.created_at} | {l.event_name} | {l.status} | Client: {l.client_id} | Err: {l.error_message}")

asyncio.run(check())
