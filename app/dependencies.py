import time
import logging
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.client import Client

logger = logging.getLogger(__name__)

# ─── In-Memory API Key Cache ────────────────────────────────────────────────
# প্রতি request-এ DB query বাদ দিতে TTL-based cache
# Key = api_key, Value = (Client object, cached_timestamp)
_client_cache: dict[str, tuple[Client, float]] = {}
CACHE_TTL = 60  # 60 সেকেন্ড — client info cache করে রাখো


async def get_current_client(
    x_api_key: str = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> Client:
    """
    প্রতিটি /events রিকোয়েস্টে X-API-Key হেডার চেক করে
    ক্লায়েন্ট ভেরিফাই করে।
    In-memory cache দিয়ে DB query minimize করে (60s TTL)।
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key প্রয়োজন। X-API-Key header পাঠান।"
        )

    # ─── Cache থেকে চেক করো আগে ─────────────────────────────────────
    now = time.time()
    if x_api_key in _client_cache:
        client, cached_at = _client_cache[x_api_key]
        if now - cached_at < CACHE_TTL:
            # Cache hit — DB query বাদ!
            if client.is_active:
                return client
            else:
                # Cache-এ আছে কিন্তু inactive — remove & reject
                del _client_cache[x_api_key]
                raise HTTPException(
                    status_code=401,
                    detail="Invalid বা Inactive API Key।"
                )

    # ─── Cache miss — DB query ─────────────────────────────────────────
    result = await db.execute(
        select(Client).where(
            Client.api_key == x_api_key,
            Client.is_active == True
        )
    )
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=401,
            detail="Invalid বা Inactive API Key।"
        )

    # ─── Cache-এ রাখো ──────────────────────────────────────────────────
    _client_cache[x_api_key] = (client, now)
    return client
