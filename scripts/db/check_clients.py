import asyncio
from app.database import AsyncSessionLocal
from app.models.client import Client
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Client.name, Client.api_key, Client.portal_key, Client.is_active))
        rows = res.all()
        for r in rows:
            print(f"Name: {r[0]}")
            print(f"  api_key:    {r[1]}")
            print(f"  portal_key: {r[2]}")
            print(f"  is_active:  {r[3]}")
            print()

if __name__ == "__main__":
    asyncio.run(main())
