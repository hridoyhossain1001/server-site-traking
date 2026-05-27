import asyncio
from app.database import AsyncSessionLocal
from app.models.failed_event import FailedEvent
from sqlalchemy import select, func

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(FailedEvent.status, func.count(FailedEvent.id)).group_by(FailedEvent.status))
        print(f"FAILED_STATS: {res.all()}")

if __name__ == "__main__":
    asyncio.run(main())
