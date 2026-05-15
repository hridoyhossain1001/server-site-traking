import json
import logging
import os
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Query
from sqlalchemy import and_, func as sql_func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, AsyncSessionLocal
from app.dependencies import get_current_client, CachedClient
from app.models.event_dedup import EventDedup
from app.models.event_log import EventLog
from app.schemas.event import EventsPayload, EventsResponse
from app.services.capi_service import send_to_facebook
from app.services.tiktok_service import send_to_tiktok
from app.services.geoip_service import get_location_data
from app.services.ga4_service import send_to_ga4
from app.services.retry_service import save_failed_event
from app.services.usage_service import check_usage_limits_db, increment_usage_counters_db
from app.models.pending_event import PendingEvent

logger = logging.getLogger(__name__)

router = APIRouter()

MAX_EVENTS_PER_REQUEST = int(os.getenv("MAX_EVENTS_PER_REQUEST", "500"))

# ─── Domain Validation Helper ────────────────────────────────────────────────
def _is_domain_allowed(request_host: str, allowed_domain: str) -> bool:
    """Check if request_host is exactly allowed_domain or a real subdomain of it."""
    if not request_host:
        return False
    return request_host == allowed_domain or request_host.endswith("." + allowed_domain)


async def reserve_unique_events(
    db: AsyncSession,
    client: CachedClient,
    events: list,
) -> list:
    """
    Reserve event IDs atomically before sending to Facebook.
    The unique index on (client_id, event_id) closes the concurrent duplicate race.
    commit/rollback এখানে করা হয় না — caller নিজে transaction manage করবে।
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

    result = await db.execute(stmt)
    reserved_ids = set(result.scalars().all())

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
    client: CachedClient = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    hold: bool = Query(False, description="True হলে Purchase event hold হবে"),
):
    """
    ক্লায়েন্টের API Key ভেরিফাই করে Facebook CAPI-তে ইভেন্ট ফরওয়ার্ড করে।
    Deduplication DB unique constraint দিয়ে atomic করা হয়েছে।

    Transaction Flow (Fixed):
    ─────────────────────────
    1. check_usage_limits_db()  → শুধু READ করে, counter বাড়ায় না
    2. reserve_unique_events()  → dedup entries INSERT করে (uncommitted)
    3. db.commit()              → একটি single commit — dedup reserve confirmed
    4. send_to_facebook()       → Facebook-এ পাঠায়
    5. increment_usage_counters_db() → সফল হলে counter বাড়ায় (নতুন session)

    এভাবে:
    - FB fail হলে dedup committed থাকে (retry service dedup bypass করে)
    - Usage counter শুধু successful send-এই বাড়ে
    - কোনো partial state থাকে না
    """
    if not payload.data:
        raise HTTPException(status_code=400, detail="ইভেন্ট ডাটা খালি!")
    if len(payload.data) > MAX_EVENTS_PER_REQUEST:
        raise HTTPException(
            status_code=413,
            detail=f"Too many events in one request. Max {MAX_EVENTS_PER_REQUEST}.",
        )

    # ─── Domain Whitelisting (API Key চুরি প্রতিরোধ) ─────────────────
    # Client-এর domain সেট করা থাকলে, শুধু সেই ডোমেইন থেকে রিকোয়েস্ট নেবে
    # urlparse দিয়ে hostname extract করে exact match বা real subdomain চেক
    if client.domain:
        origin = request.headers.get("origin", "") or ""
        referer = request.headers.get("referer", "") or ""
        allowed_domain = client.domain.lower().strip()
        origin_host = (urlparse(origin).hostname or "").lower()
        referer_host = (urlparse(referer).hostname or "").lower()
        if not (_is_domain_allowed(origin_host, allowed_domain) or _is_domain_allowed(referer_host, allowed_domain)):
            logger.warning(
                f"[{client.name}] Domain mismatch! "
                f"Allowed: {allowed_domain}, Origin: {origin_host}, Referer: {referer_host}"
            )
            raise HTTPException(
                status_code=403,
                detail="Unauthorized domain. এই API Key আপনার ডোমেইনে রেজিস্টার্ড নয়।",
            )

    # ─── Real IP Detection (Heroku/Cloudflare X-Forwarded-For হেডার থেকে) ──
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else None

    # ─── Auto-inject real IP & User-Agent into user_data ─────────────────
    # ফ্রন্টএন্ড থেকে placeholder IP (8.8.8.8) বা কোনো IP না আসলে
    # সার্ভার নিজেই ইউজারের আসল IP বসিয়ে দেবে
    PLACEHOLDER_IPS = {"8.8.8.8", "127.0.0.1", "0.0.0.0", None, ""}
    for event in payload.data:
        # Ensure user_data exists (schema now allows Optional)
        if not event.user_data:
            from app.schemas.event import UserData
            event.user_data = UserData()
        if event.user_data.client_ip_address in PLACEHOLDER_IPS:
            event.user_data.client_ip_address = client_ip
        if not event.user_data.client_user_agent:
            event.user_data.client_user_agent = request.headers.get("user-agent")

        # ─── GeoIP Enrichment ──────────────────────────────────────────
        if event.user_data.client_ip_address:
            loc_data = get_location_data(event.user_data.client_ip_address)
            if loc_data:
                from app.schemas.event import _clean_and_hash
                if loc_data.get("ct") and not event.user_data.ct:
                    event.user_data.ct = [_clean_and_hash(loc_data["ct"], "ct")]
                if loc_data.get("st") and not event.user_data.st:
                    event.user_data.st = [_clean_and_hash(loc_data["st"], "st")]
                if loc_data.get("country") and not event.user_data.country:
                    event.user_data.country = [_clean_and_hash(loc_data["country"], "country")]
                if loc_data.get("zp") and not event.user_data.zp:
                    event.user_data.zp = [_clean_and_hash(loc_data["zp"], "zp")]

    # ─── Step 1: Usage Limit CHECK (read-only, no counter increment) ──
    await check_usage_limits_db(db, client, len(payload.data))

    # ─── Step 2: Dedup reservation (uncommitted) ──────────────────────
    try:
        unique_events = await reserve_unique_events(db, client, payload.data)
        # ─── Step 3: Single commit — dedup reservation confirmed ──────
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    if not unique_events:
        return EventsResponse(
            status="success",
            events_received=0,
            message="সব ইভেন্ট আগেই পাঠানো হয়েছে (deduplicated)",
        )

    # ─── Step 3.5: Deferred Purchase — Purchase events হোল্ড করো ──────
    # ক্লায়েন্টের deferred_purchase ON থাকলে বা hold=true query param থাকলে
    # Purchase events pending_events টেবিলে সেভ হবে, Facebook-এ যাবে না
    should_hold = hold or client.deferred_purchase
    deferred_count = 0  # default — no deferred events

    if should_hold:
        deferred_events = []
        immediate_events = []

        for event in unique_events:
            if event.event_name == "Purchase":
                deferred_events.append(event)
            else:
                immediate_events.append(event)

        # Purchase events → pending_events টেবিলে সেভ
        deferred_count = 0
        for event in deferred_events:
            event_dict = event.model_dump(exclude_none=True)
            # order_id বের করো: custom_data.order_id বা event_id থেকে
            order_id = None
            if event.custom_data and hasattr(event.custom_data, 'order_id') and event.custom_data.order_id:
                order_id = event.custom_data.order_id
            elif event.event_id:
                order_id = event.event_id
            else:
                order_id = f"auto-{event.event_time}-{id(event)}"

            try:
                async with db.begin_nested():
                    pending = PendingEvent(
                        client_id=client.id,
                        order_id=order_id,
                        event_data=event_dict,
                        status="pending",
                    )
                    db.add(pending)
                    await db.flush()  # unique constraint check
                deferred_count += 1
                logger.info(f"[{client.name}] 📦 Purchase hold: {order_id}")
            except Exception as e:
                logger.warning(f"[{client.name}] Duplicate pending order: {order_id}")

        if deferred_count > 0:
            await db.commit()

        # immediate_events (non-Purchase) না থাকলে return
        if not immediate_events:
            return EventsResponse(
                status="success",
                events_received=deferred_count,
                message=f"📦 {deferred_count}টি Purchase event হোল্ড করা হয়েছে — কনফার্ম করলে Facebook-এ যাবে",
            )

        # বাকি events (PageView, AddToCart etc.) Facebook-এ পাঠাও
        unique_events = immediate_events

    event_names = ", ".join(sorted({event.event_name for event in unique_events}))

    # ─── Step 4: Send to Facebook ─────────────────────────────────────
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

    # ─── Step 5: Increment usage counters AFTER successful send ───────
    # নতুন session ব্যবহার করে — main session commit ইতিমধ্যে হয়ে গেছে
    try:
        async with AsyncSessionLocal() as usage_db:
            await increment_usage_counters_db(usage_db, client, len(unique_events))
    except Exception as e:
        # Counter increment failure should NOT fail the request
        # — event already sent to Facebook successfully
        logger.warning(f"[{client.name}] Usage counter increment failed (non-fatal): {e}")

    events_as_dicts = [event.model_dump(exclude_none=True) for event in unique_events]
    background_tasks.add_task(
        save_success_logs_bg,
        client.id,
        events_as_dicts,
        result,
        client_ip,
    )

    # ─── Step 5.5: TikTok CAPI (parallel, non-blocking) ───────────────
    if client.tiktok_pixel_id and client.tiktok_access_token:
        background_tasks.add_task(send_to_tiktok, client, unique_events)

    # ─── Step 5.6: GA4 Server-Side (parallel, non-blocking) ───────────
    if client.ga4_measurement_id and client.ga4_api_secret:
        # Dictify events for GA4 to extract standard params
        ga4_events = [evt.model_dump(exclude_none=True) for evt in unique_events]
        background_tasks.add_task(
            send_to_ga4,
            events=ga4_events,
            measurement_id=client.ga4_measurement_id,
            api_secret=client.ga4_api_secret,
            cookies=request.cookies,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent", "")
        )

    # ─── Step 5.7: Outbound Webhook (parallel, non-blocking) ──────────
    if client.webhook_url:
        from app.services.webhook_service import send_webhook
        for evt in unique_events:
            evt_dict = evt.model_dump(exclude_none=True)
            background_tasks.add_task(
                send_webhook,
                client.webhook_url,
                "event.sent",
                {
                    "client_name": client.name,
                    "event_name": evt_dict.get("event_name"),
                    "event_id": evt_dict.get("event_id"),
                    "custom_data": evt_dict.get("custom_data", {}),
                },
            )

    # Response message adjust করো — deferred events থাকলে
    total_received = len(unique_events)
    msg = "সফলভাবে Facebook-এ পাঠানো হয়েছে"
    if should_hold and deferred_count > 0:
        total_received += deferred_count
        msg = f"✅ {len(unique_events)}টি event Facebook-এ পাঠানো হয়েছে, 📦 {deferred_count}টি Purchase hold আছে"

    return EventsResponse(
        status="success",
        events_received=total_received,
        message=msg,
    )
