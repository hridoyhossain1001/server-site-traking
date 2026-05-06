import time
import logging
from dataclasses import dataclass
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.client import Client

logger = logging.getLogger(__name__)

# ─── In-Memory API Key Cache ────────────────────────────────────────────────
# প্রতি request-এ DB query বাদ দিতে TTL-based cache
# ORM object cache করলে DetachedInstanceError হতে পারে,
# তাই plain dataclass cache করা হয়। DB থেকে আনা Client-এর সব প্রয়োজনীয় field কপি করে রাখে।


@dataclass(frozen=True, slots=True)
class CachedClient:
    """Lightweight snapshot of a Client row — safe to cache across requests."""
    id: int
    name: str
    api_key: str
    pixel_id: str
    access_token: str
    test_event_code: str | None
    is_active: bool
    domain: str | None
    rate_limit: int
    daily_quota: int
    tiktok_pixel_id: str | None
    tiktok_access_token: str | None
    ga4_measurement_id: str | None
    ga4_api_secret: str | None


_client_cache: dict[str, tuple[CachedClient, float]] = {}
CACHE_TTL = 60  # 60 সেকেন্ড — client info cache করে রাখো


def _snapshot(client: Client) -> CachedClient:
    """ORM object থেকে plain dataclass তৈরি করো — session-independent।"""
    return CachedClient(
        id=client.id,
        name=client.name,
        api_key=client.api_key,
        pixel_id=client.pixel_id,
        access_token=client.access_token,
        test_event_code=client.test_event_code,
        is_active=client.is_active,
        domain=client.domain,
        rate_limit=client.rate_limit or 5000,
        daily_quota=client.daily_quota or 100000,
        tiktok_pixel_id=getattr(client, 'tiktok_pixel_id', None),
        tiktok_access_token=getattr(client, 'tiktok_access_token', None),
        ga4_measurement_id=getattr(client, 'ga4_measurement_id', None),
        ga4_api_secret=getattr(client, 'ga4_api_secret', None),
    )


async def get_current_client(
    x_api_key: str = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> CachedClient:
    """
    প্রতিটি /events রিকোয়েস্টে X-API-Key হেডার চেক করে
    ক্লায়েন্ট ভেরিফাই করে।
    In-memory cache দিয়ে DB query minimize করে (60s TTL)।
    CachedClient রিটার্ন করে — SQLAlchemy session-এ নির্ভর করে না।
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key প্রয়োজন। X-API-Key header পাঠান।"
        )

    # ─── Cache থেকে চেক করো আগে ─────────────────────────────────────
    now = time.time()
    if x_api_key in _client_cache:
        cached, cached_at = _client_cache[x_api_key]
        if now - cached_at < CACHE_TTL:
            # Cache hit — DB query বাদ!
            if cached.is_active:
                return cached
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

    # ─── Cache-এ রাখো (plain dataclass — safe across sessions) ──────
    cached = _snapshot(client)
    _client_cache[x_api_key] = (cached, now)
    return cached
