"""
Event Testing & Debug Router
──────────────────────────────
Real-time event debug, test event sender, এবং payload inspector।

Endpoints:
  POST /api/v1/debug/test-event    — Test event পাঠায় (Facebook Test Event Code সহ)
  GET  /api/v1/debug/recent        — সর্বশেষ events real-time stream
  POST /api/v1/debug/validate      — Event payload validate করে (পাঠায় না)
"""

import json
import logging
import time
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_client, CachedClient
from app.models.event_log import EventLog
from app.schemas.event import EventData

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Request/Response Schemas ────────────────────────────────────────────────

class TestEventRequest(BaseModel):
    event_name: str = "PageView"
    value: float | None = None
    currency: str | None = "BDT"
    custom_params: dict | None = None


class ValidationResult(BaseModel):
    field: str
    status: str  # ok / warning / error
    message: str


class ValidateResponse(BaseModel):
    status: str
    is_valid: bool
    emq_estimate: float
    issues: list[ValidationResult]


class TestEventResponse(BaseModel):
    status: str
    message: str
    event_id: str
    fb_response: dict | None = None


class RecentEventItem(BaseModel):
    timestamp: str
    event_name: str
    event_id: str | None
    status: str
    ip_address: str | None
    user_agent_short: str | None
    fb_response_preview: str | None
    age_seconds: float


class RecentEventsResponse(BaseModel):
    status: str
    total: int
    events: list[RecentEventItem]


# ─── POST /debug/test-event — Send Test Event ────────────────────────────────

@router.post(
    "/debug/test-event",
    response_model=TestEventResponse,
    summary="Send a test event to Facebook",
)
async def send_test_event(
    payload: TestEventRequest,
    client: CachedClient = Depends(get_current_client),
):
    """
    Facebook Test Events Tool-এ verify করার জন্য test event পাঠায়।
    Test Event Code না থাকলেও কাজ করবে।
    """
    from app.services.capi_service import send_to_facebook

    event_id = f"test_{int(time.time())}_{id(payload)}"

    # Build test event
    event_dict = {
        "event_name": payload.event_name,
        "event_time": int(datetime.now(timezone.utc).timestamp()),
        "event_id": event_id,
        "event_source_url": "https://test.example.com/debug",
        "action_source": "website",
        "user_data": {
            "client_ip_address": "127.0.0.1",
            "client_user_agent": "Buykori-AdSync-DebugTool/1.0",
            "em": ["test@example.com"],
        },
    }

    if payload.value:
        event_dict["custom_data"] = {
            "value": payload.value,
            "currency": payload.currency or "BDT",
        }

    if payload.custom_params:
        if "custom_data" not in event_dict:
            event_dict["custom_data"] = {}
        event_dict["custom_data"].update(payload.custom_params)

    try:
        event = EventData(**event_dict)
        result = await send_to_facebook(client, [event])
        logger.info(f"[{client.name}] 🧪 Test event sent: {payload.event_name}")

        return TestEventResponse(
            status="success",
            message=f"🧪 Test {payload.event_name} event সফলভাবে পাঠানো হয়েছে!",
            event_id=event_id,
            fb_response=result,
        )
    except Exception as e:
        logger.error(f"[{client.name}] Test event failed: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"Test event পাঠাতে সমস্যা: {str(e)}",
        )


# ─── GET /debug/recent — Recent Events Stream ────────────────────────────────

@router.get(
    "/debug/recent",
    response_model=RecentEventsResponse,
    summary="Recent events for debugging",
)
async def recent_events(
    client: CachedClient = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(30, ge=1, le=100),
    minutes: int = Query(60, ge=1, le=1440, description="সর্বশেষ কত মিনিটের events"),
):
    """Real-time event debugging — সর্বশেষ events দেখানো"""
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    result = await db.execute(
        select(EventLog)
        .where(and_(
            EventLog.client_id == client.id,
            EventLog.created_at >= since,
        ))
        .order_by(EventLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()

    now = datetime.now(timezone.utc)
    events = []
    for log in logs:
        created = log.created_at
        if created:
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            age = (now - created).total_seconds()
        else:
            age = 0

        # Truncate FB response for preview
        fb_preview = None
        if log.fb_response:
            try:
                fb_data = json.loads(log.fb_response) if isinstance(log.fb_response, str) else log.fb_response
                fb_preview = json.dumps(fb_data)[:200]
            except Exception:
                fb_preview = str(log.fb_response)[:200]

        events.append(RecentEventItem(
            timestamp=log.created_at.isoformat() if log.created_at else "",
            event_name=log.event_name or "unknown",
            event_id=log.event_id,
            status=log.status or "unknown",
            ip_address=log.ip_address,
            user_agent_short=None,
            fb_response_preview=fb_preview,
            age_seconds=round(age, 1),
        ))

    return RecentEventsResponse(
        status="success",
        total=len(events),
        events=events,
    )


# ─── POST /debug/validate — Validate Event Payload ──────────────────────────

@router.post(
    "/debug/validate",
    response_model=ValidateResponse,
    summary="Validate event payload without sending",
)
async def validate_event(
    event: EventData,
    client: CachedClient = Depends(get_current_client),
):
    """
    Event payload validate করে — Facebook-এ পাঠায় না।
    EMQ score estimate ও missing fields warning দেয়।
    """
    issues = []
    emq = 0.0

    # event_name check
    valid_events = [
        "PageView", "ViewContent", "AddToCart", "InitiateCheckout",
        "Purchase", "Search", "Lead", "CompleteRegistration",
        "AddPaymentInfo", "AddToWishlist", "Contact", "Subscribe",
    ]
    if event.event_name in valid_events:
        issues.append(ValidationResult(field="event_name", status="ok", message=f"✅ '{event.event_name}' is a standard FB event"))
    else:
        issues.append(ValidationResult(field="event_name", status="warning", message=f"⚠️ '{event.event_name}' is a custom event — FB may not auto-optimize"))

    # event_time check
    if event.event_time:
        now_ts = int(datetime.now(timezone.utc).timestamp())
        diff = abs(now_ts - event.event_time)
        if diff > 7 * 86400:
            issues.append(ValidationResult(field="event_time", status="error", message="❌ event_time ৭ দিনের বেশি পুরোনো — FB reject করবে"))
        elif diff > 3600:
            issues.append(ValidationResult(field="event_time", status="warning", message=f"⚠️ event_time {diff//3600} ঘণ্টা আগের"))
        else:
            issues.append(ValidationResult(field="event_time", status="ok", message="✅ event_time valid"))
    else:
        issues.append(ValidationResult(field="event_time", status="error", message="❌ event_time missing"))

    # user_data checks (EMQ factors)
    ud = event.user_data
    if ud:
        if ud.em:
            emq += 2.5
            issues.append(ValidationResult(field="user_data.em", status="ok", message="✅ Email provided (+2.5 EMQ)"))
        else:
            issues.append(ValidationResult(field="user_data.em", status="warning", message="⚠️ Email missing (-2.5 EMQ)"))

        if ud.ph:
            emq += 2.0
            issues.append(ValidationResult(field="user_data.ph", status="ok", message="✅ Phone provided (+2.0 EMQ)"))
        else:
            issues.append(ValidationResult(field="user_data.ph", status="warning", message="⚠️ Phone missing (-2.0 EMQ)"))

        if ud.client_ip_address and ud.client_ip_address not in ("8.8.8.8", "127.0.0.1", "0.0.0.0"):
            emq += 1.5
            issues.append(ValidationResult(field="user_data.ip", status="ok", message="✅ Real IP provided (+1.5 EMQ)"))
        else:
            issues.append(ValidationResult(field="user_data.ip", status="warning", message="⚠️ No real IP — server will auto-inject"))

        if ud.client_user_agent:
            emq += 1.0
            issues.append(ValidationResult(field="user_data.ua", status="ok", message="✅ User Agent provided (+1.0 EMQ)"))

        if ud.fbp:
            emq += 1.5
            issues.append(ValidationResult(field="user_data.fbp", status="ok", message="✅ FB Pixel cookie provided (+1.5 EMQ)"))
        else:
            issues.append(ValidationResult(field="user_data.fbp", status="warning", message="⚠️ fbp cookie missing — EMQ lower"))

        if ud.fbc:
            emq += 1.0
            issues.append(ValidationResult(field="user_data.fbc", status="ok", message="✅ FB Click ID provided (+1.0 EMQ)"))
    else:
        issues.append(ValidationResult(field="user_data", status="error", message="❌ user_data completely missing — EMQ 0"))

    # Purchase-specific checks
    if event.event_name == "Purchase":
        cd = event.custom_data
        if cd and hasattr(cd, 'value') and cd.value:
            issues.append(ValidationResult(field="custom_data.value", status="ok", message=f"✅ Value: {cd.value}"))
        else:
            issues.append(ValidationResult(field="custom_data.value", status="error", message="❌ Purchase event-এ value missing — FB optimization কাজ করবে না"))

        if cd and hasattr(cd, 'currency') and cd.currency:
            issues.append(ValidationResult(field="custom_data.currency", status="ok", message=f"✅ Currency: {cd.currency}"))
        else:
            issues.append(ValidationResult(field="custom_data.currency", status="warning", message="⚠️ Currency missing (default USD)"))

    emq = min(emq, 10.0)
    is_valid = not any(i.status == "error" for i in issues)

    return ValidateResponse(
        status="success",
        is_valid=is_valid,
        emq_estimate=round(emq, 1),
        issues=issues,
    )
