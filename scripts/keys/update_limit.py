import asyncio
from app.database import AsyncSessionLocal
from app.models.client import Client
from sqlalchemy import update

async def main():
    async with AsyncSessionLocal() as db:
        await db.execute(update(Client).where(Client.name == 'LoadTest').values(rate_limit=5))
        await db.commit()
        print('SUCCESS: Rate limit updated to 10')

if __name__ == "__main__":
    asyncio.run(main())
