import json
import time
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from sqlalchemy import select, and_, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.event import EventsPayload, EventsResponse
from app.dependencies import get_current_client
from app.services.capi_service import send_to_facebook
from app.models.client import Client
from app.models.event_log import EventLog
from app.database import get_db, AsyncSessionLocal
from app.services.retry_service import save_failed_event

logger = logging.getLogger(__name__)

router = APIRouter()


# ─── In-Memory Rate Limiting ────────────────────────────────────────────────
# DB query বাদ দিয়ে memory-তে count রাখো (per worker)
# Key = client_id, Value = list of timestamps
_rate_counters: dict[int, list[float]] = defaultdict(list)
_daily_counters: dict[int, tuple[str, int]] = {}  # (date_str, count)


def check_rate_limit(client_id: int, rate_limit: int, event_count: int) -> bool:
    """In-memory rate limit check — DB query বাদ! O(n) cleanup + O(1) check"""
    now = time.time()
    # 60 সেকেন্ডের পুরাতন entries বাদ দাও
    _rate_counters[client_id] = [
        t for t in _rate_counters[client_id] if now - t < 60
    ]
    if len(_rate_counters[client_id]) + event_count > rate_limit:
        return False
    _rate_counters[client_id].extend([now] * event_count)
    return True


def check_daily_quota(client_id: int, daily_quota: int | None, event_count: int) -> bool:
    """In-memory daily quota check — DB query বাদ!"""
    if not daily_quota:
        return True

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if client_id in _daily_counters:
        stored_date, count = _daily_counters[client_id]
        if stored_date != today:
            # নতুন দিন — reset
            _daily_counters[client_id] = (today, event_count)
            return True
        if count + event_count > daily_quota:
            return False
        _daily_counters[client_id] = (today, count + event_count)
    else:
        _daily_counters[client_id] = (today, event_count)

    return True


# ─── Background DB Write Function ───────────────────────────────────────────
async def save_event_logs(
    client_id: int,
    events: list,
    fb_result: dict | None,
    client_ip: str | None,
):
    """
    Background task — response পাঠানোর পর DB-তে event log লেখে।
    Client-কে অপেক্ষা করাতে হয় না!
    """
    try:
        async with AsyncSessionLocal() as db:
            log_entries = [
                EventLog(
                    client_id=client_id,
                    event_name=ev.event_name,
                    event_id=ev.event_id,
                    event_count=1,
                    status="success",
                    fb_response=json.dumps(fb_result) if fb_result else None,
                    ip_address=client_ip,
                )
                for ev in events
            ]
            db.add_all(log_entries)  # Bulk insert — একটা query-তে সব!
            await db.commit()
    except Exception as e:
        logger.error(f"Background log save error: {e}")


async def save_error_log_bg(
    client_id: int,
    event_names: str,
    event_count: int,
    error_msg: str,
    client_ip: str | None,
    events_data: list,
):
    """Background task — error log + retry queue save"""
    try:
        async with AsyncSessionLocal() as db:
            log_entry = EventLog(
                client_id=client_id,
                event_name=event_names,
                event_count=event_count,
                status="failed",
                error_message=error_msg[:500],
                ip_address=client_ip,
            )
            db.add(log_entry)
            await db.commit()

            # Retry queue-তে সেভ করো
            await save_failed_event(db, client_id, events_data, error_msg)
    except Exception as e:
        logger.error(f"Background error log save failed: {e}")


@router.post(
    "/events",
    response_model=EventsResponse,
    summary="Facebook CAPI Events Endpoint",
)
async def receive_events(
    request: Request,
    payload: EventsPayload,
    background_tasks: BackgroundTasks,
    client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
):
    """
    ক্লায়েন্টের API Key ভেরিফাই করে Facebook CAPI-তে ইভেন্ট ফরওয়ার্ড করে।
    
    🚀 Optimizations:
    - Batch deduplication (N queries → 1)
    - In-memory rate limiting (DB query বাদ)
    - Background DB writes (response আগে, write পরে)
    - Bulk insert (N inserts → 1)
    """
    if not payload.data:
        raise HTTPException(status_code=400, detail="ইভেন্ট ডাটা খালি!")

    client_ip = request.client.host if request.client else None

    # ─── In-Memory Rate Limit Check (DB query বাদ!) ───────────────────
    rate_limit = client.rate_limit or 5000
    if not check_rate_limit(client.id, rate_limit, len(payload.data)):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded! Max {rate_limit} events/min"
        )

    # ─── In-Memory Daily Quota Check (DB query বাদ!) ──────────────────
    if not check_daily_quota(client.id, client.daily_quota, len(payload.data)):
        raise HTTPException(
            status_code=429,
            detail=f"Daily quota exceeded! Max {client.daily_quota} events/day"
        )

    # ─── Batch Deduplication: একটা query-তে সব event_id চেক (N→1) ────
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    event_ids = [e.event_id for e in payload.data if e.event_id]

    existing_ids: set = set()
    if event_ids:
        existing_result = await db.execute(
            select(EventLog.event_id).where(
                and_(
                    EventLog.client_id == client.id,
                    EventLog.event_id.in_(event_ids),
                    EventLog.status == "success",
                    EventLog.created_at >= cutoff,
                )
            )
        )
        existing_ids = set(existing_result.scalars().all())

    # Unique events filter করো
    unique_events = []
    for event in payload.data:
        if event.event_id and event.event_id in existing_ids:
            logger.info(f"[{client.name}] Duplicate event skipped: {event.event_id}")
            continue
        unique_events.append(event)

    if not unique_events:
        return EventsResponse(
            status="success",
            events_received=0,
            message="সব ইভেন্ট আগেই পাঠানো হয়েছে (deduplicated)"
        )

    event_names = ", ".join(set(e.event_name for e in unique_events))

    try:
        # CAPI সার্ভিসে ডাটা পাঠানো (persistent HTTP client ব্যবহার করে)
        result = await send_to_facebook(client, unique_events)

        # ✅ Background-এ DB write করো — client-কে অপেক্ষা করাতে হবে না!
        background_tasks.add_task(
            save_event_logs, client.id, unique_events, result, client_ip
        )

        return EventsResponse(
            status="success",
            events_received=len(unique_events),
            message="সফলভাবে Facebook-এ পাঠানো হয়েছে"
        )

    except Exception as e:
        # ❌ ব্যর্থ হলে error log + retry queue (background-এ)
        error_msg = str(e)
        logger.error(f"Client {client.name} | Error: {error_msg}")

        events_as_dicts = [ev.model_dump(exclude_none=True) for ev in unique_events]
        background_tasks.add_task(
            save_error_log_bg,
            client.id, event_names, len(unique_events),
            error_msg, client_ip, events_as_dicts
        )

        raise HTTPException(
            status_code=502,
            detail="Facebook API তে সমস্যা — ইভেন্ট retry queue-তে রাখা হয়েছে"
        )
