import asyncio
import os
from app.database import AsyncSessionLocal
from app.models.client import Client
from app.security import encrypt_token

def mask_key(value: str) -> str:
    return f"{value[:8]}...{value[-4:]}"

async def run():
    access_token = os.getenv("CAPI_ACCESS_TOKEN")
    if not access_token:
        raise SystemExit("Set CAPI_ACCESS_TOKEN before creating a client.")

    async with AsyncSessionLocal() as db:
        c = Client(
            name=os.getenv("CAPI_CLIENT_NAME", "Load Test"),
            pixel_id=os.getenv("CAPI_PIXEL_ID", "1234"),
            access_token=encrypt_token(access_token),
            rate_limit=int(os.getenv("CAPI_RATE_LIMIT", "5000")),
            daily_quota=int(os.getenv("CAPI_DAILY_QUOTA", "100000")),
        )
        db.add(c)
        await db.commit()
        await db.refresh(c)
        print("API_KEY_MASKED:" + mask_key(c.api_key))
        print("Open the admin instructions page to copy the full key securely.")

if __name__ == "__main__":
    asyncio.run(run())
