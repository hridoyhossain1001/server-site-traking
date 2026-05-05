import asyncio
from app.database import AsyncSessionLocal
from app.models.client import Client
from sqlalchemy import select

def mask_key(value: str) -> str:
    return f"{value[:8]}...{value[-4:]}"

async def run():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Client).order_by(Client.id.desc()).limit(1))
        c = res.scalar()
        if c:
            print("FOUND_KEY_MASKED:" + mask_key(c.api_key))
            print("Open the admin instructions page to copy the full key securely.")
        else:
            print("NO_CLIENT")

asyncio.run(run())
