import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.models.client import Client
from app.database import SQLALCHEMY_DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_key():
    client_name = os.getenv("CLIENT_NAME", "My Own website")
    async with async_session() as db:
        res = await db.execute(select(Client.api_key).where(Client.name.ilike(f"%{client_name}%")))
        key = res.scalars().first()
        print(f"KEY={key or ''}")

if __name__ == "__main__":
    asyncio.run(get_key())
