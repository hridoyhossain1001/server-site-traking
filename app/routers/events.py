import json
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy import and_, func as sql_func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, AsyncSessionLocal
from app.dependencies import get_current_client
from app.models.client import Client
from app.models.event_dedup import EventDedup
from app.models.event_log import EventLog
from app.schemas.event import EventsPayload, EventsResponse
from app.services.capi_service import send_to_facebook
from app.services.retry_service import save_failed_event

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_EVENTS_PER_REQUEST = int(os.getenv("MAX_EVENTS_PER_REQUEST", "500"))

_rate_counters: dict[int, list[float]] = defaultdict(list)
_daily_counters: dict[int, tuple[str, int]] = {}  # (date_str, count)

def enforce_usage_limits(
    client: Client,
    incoming_event_count: int,
) -> None:
    """In-memory rate limit and daily quota checks."""
    rate_limit = client.rate_limit or 5000
    now = time.time()
    
    # 60 সেকেন্ডের পুরানো এন্ট্রি মুছে ফেলো
    _rate_counters[client.id] = [
        t for t in _rate_counters[client.id] if now - t < 60
    ]
    
    recent_count = len(_rate_counters[client.id])
    if recent_count + incoming_event_count > rate_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded! {recent_count}/{rate_limit} events/min",
        )
    _rate_counters[client.id].extend([now] * incoming_event_count)

    if client.daily_quota:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if client.id in _daily_counters:
            stored_date, count = _daily_counters[client.id]
            if stored_date != today:
                _daily_counters[client.id] = (today, incoming_event_count)
            else:
                if count + incoming_event_count > client.daily_quota:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Daily quota exceeded! Today {count}/{client.daily_quota} events sent.",
                    )
                _daily_counters[client.id] = (today, count + incoming_event_count)
        else:
            _daily_counters[client.id] = (today, incoming_event_count)


async def reserve_unique_events(
    db: AsyncSession,
    client: Client,
    events: list,
) -> list:
    """
    Reserve event IDs atomically before sending to Facebook.
    The unique index on (client_id, event_id) closes the concurrent duplicate race.
    """
    candidate_ids: list[str] = []
    seen_ids: set[str] = set()
    for event in events:
        if not event.event_id or event.event_id in seen_ids:
            continue
        seen_ids.add(event.event_id)
        candidate_ids.append(event.event_id)

    if not candidate_ids:
        return [event for event in events if not event.event_id]

    rows = [{"client_id": client.id, "event_id": event_id} for event_id in candidate_ids]
    stmt = (
        pg_insert(EventDedup)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["client_id", "event_id"])
        .returning(EventDedup.event_id)
    )

    try:
        result = await db.execute(stmt)
        reserved_ids = set(result.scalars().all())
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    unique_events = []
    accepted_ids: set[str] = set()
    for event in events:
        if not event.event_id:
            unique_events.append(event)
            continue
        if event.event_id in accepted_ids:
            logger.info(f"[{client.name}] Duplicate event skipped in request: {event.event_id}")
            continue
        accepted_ids.add(event.event_id)
        if event.event_id not in reserved_ids:
            logger.info(f"[{client.name}] Duplicate event skipped: {event.event_id}")
            continue
        unique_events.append(event)

    return unique_events


async def save_success_logs_bg(
    client_id: int,
    events_data: list,
    fb_result: dict | None,
    client_ip: str | None,
) -> None:
    try:
        async with AsyncSessionLocal() as db:
            log_entries = [
                EventLog(
                    client_id=client_id,
                    event_name=event.get("event_name") or "unknown",
                    event_id=event.get("event_id"),
                    event_count=1,
                    status="success",
                    fb_response=json.dumps(fb_result) if fb_result else None,
                    ip_address=client_ip,
                )
                for event in events_data
            ]
            db.add_all(log_entries)
            await db.commit()
    except Exception as e:
        logger.error(f"Background success log save error: {e}")


async def save_failure_log_and_retry_bg(
    client_id: int,
    event_names: str,
    events_data: list,
    error_msg: str,
    client_ip: str | None,
) -> None:
    try:
        async with AsyncSessionLocal() as db:
            log_entry = EventLog(
                client_id=client_id,
                event_name=event_names,
                event_count=len(events_data),
                status="failed",
                error_message=error_msg[:500],
                ip_address=client_ip,
            )
            db.add(log_entry)
            await db.commit()

            saved = await save_failed_event(db, client_id, events_data, error_msg)
            if not saved:
                logger.error(f"[Client {client_id}] Failed events were not saved to retry queue.")
    except Exception as e:
        logger.error(f"Background failure log save error: {e}")


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
    Deduplication DB unique constraint দিয়ে atomic করা হয়েছে।
    """
    if not payload.data:
        raise HTTPException(status_code=400, detail="ইভেন্ট ডাটা খালি!")
    if len(payload.data) > MAX_EVENTS_PER_REQUEST:
        raise HTTPException(
            status_code=413,
            detail=f"Too many events in one request. Max {MAX_EVENTS_PER_REQUEST}.",
        )

    client_ip = request.client.host if request.client else None

    enforce_usage_limits(client, len(payload.data))
    unique_events = await reserve_unique_events(db, client, payload.data)

    if not unique_events:
        return EventsResponse(
            status="success",
            events_received=0,
            message="সব ইভেন্ট আগেই পাঠানো হয়েছে (deduplicated)",
        )

    event_names = ", ".join(sorted({event.event_name for event in unique_events}))

    try:
        result = await send_to_facebook(client, unique_events)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Client {client.name} | Error: {error_msg}")

        events_as_dicts = [event.model_dump(exclude_none=True) for event in unique_events]
        background_tasks.add_task(
            save_failure_log_and_retry_bg,
            client.id,
            event_names,
            events_as_dicts,
            error_msg,
            client_ip,
        )

        raise HTTPException(
            status_code=502,
            detail="Facebook API তে সমস্যা — ইভেন্ট retry queue-তে রাখা হয়েছে",
        ) from e

    events_as_dicts = [event.model_dump(exclude_none=True) for event in unique_events]
    background_tasks.add_task(
        save_success_logs_bg,
        client.id,
        events_as_dicts,
        result,
        client_ip,
    )

    return EventsResponse(
        status="success",
        events_received=len(unique_events),
        message="সফলভাবে Facebook-এ পাঠানো হয়েছে",
    )
