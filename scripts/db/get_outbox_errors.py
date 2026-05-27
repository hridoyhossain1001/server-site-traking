import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models.event_outbox import EventOutbox
from app.database import DATABASE_URL

db_url = DATABASE_URL

engine = create_async_engine(db_url)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def check_stuck():
    async with async_session() as db:
        res = await db.execute(select(EventOutbox).where(EventOutbox.status != 'sent'))
        rows = res.scalars().all()
        print(f"Total pending outbox rows: {len(rows)}")
        for r in rows:
            print("====================================")
            print(f"ID: {r.id}")
            print(f"Client ID: {r.client_id}")
            print(f"Status: {r.status}")
            print(f"Attempts: {r.attempts}")
            print(f"Next attempt: {r.next_attempt_at}")
            print(f"Last error: {r.last_error}")
            print(f"Payload event: {r.event_payload[0].get('event_name') if r.event_payload and len(r.event_payload) > 0 else 'None'}")
            print(f"Payload ID: {r.event_payload[0].get('event_id') if r.event_payload and len(r.event_payload) > 0 else 'None'}")
            print(f"Full payload: {r.event_payload}")

if __name__ == "__main__":
    asyncio.run(check_stuck())
