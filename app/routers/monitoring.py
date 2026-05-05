"""
Monitoring Router — সিস্টেম স্বাস্থ্য পরীক্ষা, ক্লায়েন্ট ড্যাশবোর্ড স্ট্যাটস,
এবং Facebook API কানেক্টিভিটি চেক।
"""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.database import get_db
from app.models.client import Client
from app.models.event_log import EventLog
from app.models.failed_event import FailedEvent
from app.routers.admin import verify_admin

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(verify_admin)])


@router.get("/health/detailed", tags=["Monitoring"])
async def detailed_health(db: AsyncSession = Depends(get_db)):
    """সিস্টেমের বিস্তারিত স্বাস্থ্য রিপোর্ট"""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # DB connectivity
    try:
        await db.execute(select(func.count(Client.id)))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    # Total clients
    clients_result = await db.execute(
        select(func.count(Client.id)).where(Client.is_active == True)
    )
    active_clients = clients_result.scalar() or 0

    # Today's events
    today_events = await db.execute(
        select(func.coalesce(func.sum(EventLog.event_count), 0)).where(
            and_(EventLog.status == "success", EventLog.created_at >= today_start)
        )
    )
    events_today = today_events.scalar() or 0

    # Failed events (today)
    today_failed = await db.execute(
        select(func.count(EventLog.id)).where(
            and_(EventLog.status == "failed", EventLog.created_at >= today_start)
        )
    )
    failed_today = today_failed.scalar() or 0

    # Pending retries
    pending_retries = await db.execute(
        select(func.count(FailedEvent.id)).where(
            FailedEvent.status.in_(["pending", "retrying"])
        )
    )
    retries_pending = pending_retries.scalar() or 0

    # Success rate
    total = events_today + failed_today
    success_rate = round((events_today / total * 100), 1) if total > 0 else 100.0

    return {
        "status": "running",
        "timestamp": now.isoformat(),
        "database": db_status,
        "active_clients": active_clients,
        "today": {
            "events_sent": events_today,
            "events_failed": failed_today,
            "success_rate": f"{success_rate}%",
        },
        "retry_queue": {
            "pending": retries_pending,
        },
    }


@router.get("/health/facebook", tags=["Monitoring"])
async def facebook_health():
    """Facebook Graph API কানেক্টিভিটি চেক"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://graph.facebook.com/v20.0/")
            return {
                "facebook_api": "reachable",
                "response_code": response.status_code,
                "latency_ms": round(response.elapsed.total_seconds() * 1000, 1),
            }
    except Exception as e:
        return {
            "facebook_api": "unreachable",
            "error": str(e)[:200],
        }


@router.get("/stats/clients", tags=["Monitoring"])
async def client_stats(db: AsyncSession = Depends(get_db)):
    """প্রতিটি ক্লায়েন্টের আজকের ইভেন্ট স্ট্যাটিস্টিক্স"""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    clients_result = await db.execute(select(Client).where(Client.is_active == True))
    clients = clients_result.scalars().all()

    stats = []
    for c in clients:
        # আজকের সফল ইভেন্ট
        success = await db.execute(
            select(func.coalesce(func.sum(EventLog.event_count), 0)).where(
                and_(
                    EventLog.client_id == c.id,
                    EventLog.status == "success",
                    EventLog.created_at >= today_start,
                )
            )
        )
        # আজকের ব্যর্থ ইভেন্ট
        failed = await db.execute(
            select(func.count(EventLog.id)).where(
                and_(
                    EventLog.client_id == c.id,
                    EventLog.status == "failed",
                    EventLog.created_at >= today_start,
                )
            )
        )

        success_count = success.scalar() or 0
        failed_count = failed.scalar() or 0

        stats.append({
            "client": c.name,
            "pixel_id": c.pixel_id,
            "events_today": success_count,
            "errors_today": failed_count,
            "daily_quota": c.daily_quota,
            "quota_used": f"{round(success_count / c.daily_quota * 100, 1)}%" if c.daily_quota else "N/A",
        })

    return {"clients": stats}
