import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from app.models.event_outbox import EventOutbox
from app.database import DATABASE_URL

db_url = DATABASE_URL

engine = create_async_engine(db_url)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def reset_stuck():
    async with async_session() as db:
        # Reset any stuck 'processing' rows back to 'queued' and clear locks
        stmt = (
            update(EventOutbox)
            .where(EventOutbox.status == 'processing')
            .values(status='queued', locked_at=None, locked_by=None, attempts=0)
        )
        result = await db.execute(stmt)
        await db.commit()
        print(f"Successfully reset {result.rowcount} stuck outbox rows.")

if __name__ == "__main__":
    asyncio.run(reset_stuck())
