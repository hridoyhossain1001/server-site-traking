"""
Advanced Analytics Router
──────────────────────────
EMQ Score, Conversion Funnel, Event Breakdown, Hourly Heatmap, Top Products
Client Portal-এর জন্য analytics data API।

Endpoints:
  GET /api/v1/analytics/overview     — Overall stats (EMQ, funnel, breakdown)
  GET /api/v1/analytics/hourly       — Hourly heatmap data
  GET /api/v1/analytics/top-products — Top products by events
  GET /api/v1/analytics/export       — CSV export
"""

import csv
import io
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, and_, func as sql_func, extract, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_client, CachedClient
from app.models.event_log import EventLog

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Response Schemas ────────────────────────────────────────────────────────

class EventBreakdown(BaseModel):
    event_name: str
    count: int
    percentage: float


class FunnelStep(BaseModel):
    step: str
    count: int
    drop_off: float  # % drop from previous step


class HourlyData(BaseModel):
    hour: int
    count: int


class TopProduct(BaseModel):
    product_id: str
    event_count: int
    total_value: float


class CampaignRow(BaseModel):
    source: str
    campaign: str
    view_content: int
    add_to_cart: int
    initiate_checkout: int
    purchase: int
    revenue: float


class OverviewResponse(BaseModel):
    status: str
    period_days: int
    total_events: int
    success_count: int
    failed_count: int
    success_rate: float
    avg_daily_events: float
    emq_score: Optional[float] = None
    event_breakdown: list[EventBreakdown]
    funnel: list[FunnelStep]


class HourlyResponse(BaseModel):
    status: str
    data: list[HourlyData]


class TopProductsResponse(BaseModel):
    status: str
    products: list[TopProduct]


class CampaignsResponse(BaseModel):
    status: str
    campaigns: list[CampaignRow]


class SignalIssue(BaseModel):
    severity: str
    title: str
    metric: str
    impact: str
    fix: str


class SignalDoctorResponse(BaseModel):
    status: str
    period_days: int
    score: int
    grade: str
    total_events: int
    platform_readiness: dict
    signal_rates: dict
    event_counts: dict
    issues: list[SignalIssue]


# ─── EMQ Score Calculator ────────────────────────────────────────────────────

def _calculate_emq_estimate(events_data: list[dict]) -> float:
    """
    Facebook Event Match Quality (EMQ) স্কোর estimate করে।
    EMQ depends on: email, phone, IP, UA, fbp, fbc, external_id, country, city
    Score: 0-10 (higher = better match quality)
    """
    if not events_data:
        return 0.0

    total_score = 0
    for event in events_data:
        score = 0
        ud = event.get("user_data", {}) if isinstance(event, dict) else {}

        if ud.get("em"):
            score += 2.5  # Email = highest weight
        if ud.get("ph"):
            score += 2.0  # Phone
        if ud.get("client_ip_address"):
            score += 1.5  # IP
        if ud.get("client_user_agent"):
            score += 1.0  # User Agent
        if ud.get("fbp"):
            score += 1.5  # FB Pixel cookie
        if ud.get("fbc"):
            score += 1.0  # FB Click ID
        if ud.get("external_id"):
            score += 0.5  # External ID

        total_score += min(score, 10.0)

    return round(total_score / len(events_data), 1)


def _pct(part: int | float, total: int | float) -> float:
    return round((part / total * 100) if total else 0.0, 1)


def _grade(score: int) -> str:
    if score >= 90:
        return "Excellent"
    if score >= 75:
        return "Good"
    if score >= 55:
        return "Needs Work"
    return "Critical"


# ─── GET /analytics/overview ─────────────────────────────────────────────────

@router.get(
    "/analytics/overview",
    response_model=OverviewResponse,
    summary="Analytics overview — EMQ, funnel, breakdown",
)
async def analytics_overview(
    client: CachedClient = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=90, description="কত দিনের ডেটা"),
):
    """EMQ Score, Event Breakdown, Conversion Funnel সহ analytics overview"""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)

    # Total success/failed
    stats_r = await db.execute(
        select(EventLog.status, sql_func.sum(EventLog.event_count))
        .where(and_(
            EventLog.client_id == client.id,
            EventLog.created_at >= start,
        ))
        .group_by(EventLog.status)
    )
    success = 0
    failed = 0
    for row in stats_r:
        if row[0] == "success":
            success = row[1] or 0
        elif row[0] == "failed":
            failed = row[1] or 0
    total = success + failed
    rate = round((success / total * 100) if total > 0 else 0, 1)

    # Event Breakdown
    breakdown_r = await db.execute(
        select(EventLog.event_name, sql_func.sum(EventLog.event_count))
        .where(and_(
            EventLog.client_id == client.id,
            EventLog.status == "success",
            EventLog.created_at >= start,
        ))
        .group_by(EventLog.event_name)
        .order_by(sql_func.sum(EventLog.event_count).desc())
    )
    breakdown = []
    for row in breakdown_r:
        name = row[0] or "Unknown"
        count = row[1] or 0
        pct = round((count / success * 100) if success > 0 else 0, 1)
        breakdown.append(EventBreakdown(event_name=name, count=count, percentage=pct))

    # Conversion Funnel — single query instead of N+1 per event type
    funnel_events = ["PageView", "ViewContent", "AddToCart", "InitiateCheckout", "Purchase"]
    funnel_r = await db.execute(
        select(EventLog.event_name, sql_func.coalesce(sql_func.sum(EventLog.event_count), 0))
        .where(and_(
            EventLog.client_id == client.id,
            EventLog.event_name.in_(funnel_events),
            EventLog.status == "success",
            EventLog.created_at >= start,
        ))
        .group_by(EventLog.event_name)
    )
    funnel_counts = {fe: 0 for fe in funnel_events}
    for row in funnel_r:
        funnel_counts[row[0]] = row[1] or 0

    funnel = []
    prev_count = None
    for fe in funnel_events:
        count = funnel_counts[fe]
        if prev_count is not None and prev_count > 0:
            drop = round((1 - count / prev_count) * 100, 1)
        else:
            drop = 0.0
        funnel.append(FunnelStep(step=fe, count=count, drop_off=drop))
        prev_count = count if count > 0 else prev_count

    # EMQ Score — average stored estimate from recent events
    sample_r = await db.execute(
        select(sql_func.avg(EventLog.emq_score))
        .where(and_(
            EventLog.client_id == client.id,
            EventLog.status == "success",
            EventLog.emq_score.is_not(None),
            EventLog.created_at >= now - timedelta(hours=24),
        ))
    )
    emq_avg = sample_r.scalar()
    emq_score = round(float(emq_avg), 1) if emq_avg is not None else None

    return OverviewResponse(
        status="success",
        period_days=days,
        total_events=total,
        success_count=success,
        failed_count=failed,
        success_rate=rate,
        avg_daily_events=round(total / max(days, 1), 0),
        emq_score=emq_score,
        event_breakdown=breakdown,
        funnel=funnel,
    )


# ─── GET /analytics/hourly — Hourly Heatmap ─────────────────────────────────

@router.get(
    "/analytics/hourly",
    response_model=HourlyResponse,
    summary="Hourly event distribution",
)
async def analytics_hourly(
    client: CachedClient = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=30),
):
    """কোন সময়ে সবচেয়ে বেশি event fire হয়"""
    start = datetime.now(timezone.utc) - timedelta(days=days)

    hourly_r = await db.execute(
        select(
            extract("hour", EventLog.created_at).label("hour"),
            sql_func.sum(EventLog.event_count),
        )
        .where(and_(
            EventLog.client_id == client.id,
            EventLog.status == "success",
            EventLog.created_at >= start,
        ))
        .group_by("hour")
        .order_by("hour")
    )

    hourly_map = {int(r[0]): int(r[1]) for r in hourly_r}
    data = [HourlyData(hour=h, count=hourly_map.get(h, 0)) for h in range(24)]

    return HourlyResponse(status="success", data=data)


# ─── GET /analytics/top-products ─────────────────────────────────────────────

@router.get(
    "/analytics/top-products",
    response_model=TopProductsResponse,
    summary="Top products by event count",
)
async def analytics_top_products(
    client: CachedClient = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
):
    """কোন product সবচেয়ে বেশি AddToCart / Purchase হচ্ছে"""
    start = datetime.now(timezone.utc) - timedelta(days=days)

    # Extract product ID from event_id (WP snippet uses 'view-123', 'cart-123')
    # Using Postgres split_part to get the part after the hyphen
    product_id_expr = sql_func.split_part(EventLog.event_id, '-', 2)

    result = await db.execute(
        select(
            product_id_expr,
            sql_func.count(EventLog.id),
            sql_func.coalesce(sql_func.sum(EventLog.value), 0.0),
        )
        .where(and_(
            EventLog.client_id == client.id,
            EventLog.status == "success",
            EventLog.event_name.in_(["AddToCart", "ViewContent"]),
            product_id_expr != "",
            EventLog.created_at >= start,
        ))
        .group_by(product_id_expr)
        .order_by(sql_func.count(EventLog.id).desc())
        .limit(limit)
    )

    products = []
    for row in result:
        pid = row[0]
        # Ignore timestamps or random strings if they're too long
        if not pid or len(pid) > 15:
            continue

        products.append(TopProduct(
            product_id=f"Product #{pid}",
            event_count=row[1] or 0,
            total_value=float(row[2] or 0),
        ))

    return TopProductsResponse(status="success", products=products)


@router.get(
    "/analytics/campaigns",
    response_model=CampaignsResponse,
    summary="UTM campaign performance",
)
async def analytics_campaigns(
    client: CachedClient = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=180),
    limit: int = Query(50, ge=1, le=200),
):
    """Campaign-wise funnel and revenue from stored UTM attribution."""
    start = datetime.now(timezone.utc) - timedelta(days=days)
    source_expr = sql_func.coalesce(EventLog.utm_source, EventLog.campaign_source, "direct")
    campaign_expr = sql_func.coalesce(EventLog.utm_campaign, "(not set)")
    revenue_expr = sql_func.coalesce(
        sql_func.sum(case((EventLog.event_name == "Purchase", EventLog.value), else_=0)),
        0.0,
    )

    result = await db.execute(
        select(
            source_expr.label("source"),
            campaign_expr.label("campaign"),
            sql_func.coalesce(sql_func.sum(case((EventLog.event_name == "ViewContent", EventLog.event_count), else_=0)), 0),
            sql_func.coalesce(sql_func.sum(case((EventLog.event_name == "AddToCart", EventLog.event_count), else_=0)), 0),
            sql_func.coalesce(sql_func.sum(case((EventLog.event_name == "InitiateCheckout", EventLog.event_count), else_=0)), 0),
            sql_func.coalesce(sql_func.sum(case((EventLog.event_name == "Purchase", EventLog.event_count), else_=0)), 0),
            revenue_expr,
        )
        .where(and_(
            EventLog.client_id == client.id,
            EventLog.status == "success",
            EventLog.created_at >= start,
        ))
        .group_by(source_expr, campaign_expr)
        .order_by(revenue_expr.desc())
        .limit(limit)
    )

    campaigns = [
        CampaignRow(
            source=row[0] or "direct",
            campaign=row[1] or "(not set)",
            view_content=int(row[2] or 0),
            add_to_cart=int(row[3] or 0),
            initiate_checkout=int(row[4] or 0),
            purchase=int(row[5] or 0),
            revenue=float(row[6] or 0),
        )
        for row in result
    ]
    return CampaignsResponse(status="success", campaigns=campaigns)


@router.get(
    "/analytics/signal-doctor",
    response_model=SignalDoctorResponse,
    summary="Signal Health Doctor — event quality diagnostics",
)
async def signal_doctor(
    client: CachedClient = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=90),
):
    """Diagnose Facebook/TikTok/GA4 signal quality from recently delivered events."""
    start = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(EventLog)
        .where(and_(
            EventLog.client_id == client.id,
            EventLog.status == "success",
            EventLog.created_at >= start,
        ))
        .order_by(EventLog.created_at.desc())
        .limit(5000)
    )
    logs = result.scalars().all()
    total = sum(int(log.event_count or 1) for log in logs)
    event_counts: dict[str, int] = {}
    for log in logs:
        name = log.event_name or "Unknown"
        event_counts[name] = event_counts.get(name, 0) + int(log.event_count or 1)

    commerce_events = {"ViewContent", "AddToCart", "ViewCart", "RemoveFromCart", "InitiateCheckout", "AddPaymentInfo", "Purchase"}
    commerce_logs = [log for log in logs if log.event_name in commerce_events]
    purchase_logs = [log for log in logs if log.event_name == "Purchase"]

    def rate(attr: str, source=None) -> float:
        source = logs if source is None else source
        source_total = sum(int(log.event_count or 1) for log in source)
        good = sum(int(log.event_count or 1) for log in source if bool(getattr(log, attr, False)))
        return _pct(good, source_total)

    signal_rates = {
        "event_id": rate("has_event_id"),
        "user_match": rate("has_user_match"),
        "email_or_phone": rate("has_email_phone"),
        "click_id": rate("has_click_id"),
        "content_ids": rate("has_content_ids", commerce_logs),
        "contents": rate("has_contents", commerce_logs),
        "value": rate("has_value", purchase_logs or commerce_logs),
        "currency": rate("has_currency", purchase_logs or commerce_logs),
        "utm": rate("has_utm"),
    }

    if total == 0:
        return SignalDoctorResponse(
            status="success",
            period_days=days,
            score=0,
            grade="No Data",
            total_events=0,
            platform_readiness={"facebook": 0, "tiktok": 0, "ga4": 0},
            signal_rates=signal_rates,
            event_counts={},
            issues=[
                SignalIssue(
                    severity="critical",
                    title="No events received",
                    metric="0 events",
                    impact="Facebook/TikTok/GA4 কোনো platform-ই optimize করার মতো signal পাচ্ছে না।",
                    fix="WordPress plugin/API key/domain setup চেক করে একটি PageView এবং Purchase test event পাঠান।",
                )
            ],
        )

    issues: list[SignalIssue] = []
    score = 100

    if signal_rates["event_id"] < 95:
        score -= 12
        issues.append(SignalIssue(
            severity="high",
            title="Event ID coverage low",
            metric=f"{signal_rates['event_id']}%",
            impact="Browser/server deduplication দুর্বল হতে পারে, একই conversion double count হওয়ার ঝুঁকি থাকে।",
            fix="Official plugin বা tracker ব্যবহার করুন; server এখন missing event_id auto-generate করবে।",
        ))

    if commerce_logs and signal_rates["content_ids"] < 95:
        score -= 18
        issues.append(SignalIssue(
            severity="high",
            title="Content ID missing in commerce events",
            metric=f"{signal_rates['content_ids']}%",
            impact="TikTok/Facebook catalog product matching দুর্বল হবে, shop ads optimization কমে যাবে।",
            fix="Product ID/SKU থেকে content_ids পাঠান। Booster content_ids থেকে contents auto-build করবে, কিন্তু source payload-এ product ID থাকা জরুরি।",
        ))

    if purchase_logs and (signal_rates["value"] < 95 or signal_rates["currency"] < 95):
        score -= 14
        issues.append(SignalIssue(
            severity="high",
            title="Purchase value/currency incomplete",
            metric=f"value {signal_rates['value']}%, currency {signal_rates['currency']}%",
            impact="ROAS, revenue এবং value optimization ভুল দেখাতে পারে।",
            fix="Purchase custom_data-তে value এবং ISO currency দিন। Value থাকলে server default currency auto-fill করবে।",
        ))

    if signal_rates["user_match"] < 80:
        score -= 14
        issues.append(SignalIssue(
            severity="medium",
            title="User match signal weak",
            metric=f"{signal_rates['user_match']}%",
            impact="EMQ/Event Match Quality কমে যেতে পারে, conversion attribution কম match হবে।",
            fix="Email/phone capture enable রাখুন এবং browser cookies (_fbp/_fbc/_ttp/ttclid) pass হচ্ছে কি না দেখুন।",
        ))

    if signal_rates["email_or_phone"] < 30:
        score -= 8
        issues.append(SignalIssue(
            severity="medium",
            title="Email/phone signal low",
            metric=f"{signal_rates['email_or_phone']}%",
            impact="Purchase/Lead match quality কম হতে পারে, বিশেষ করে COD/ecommerce orders-এ।",
            fix="Checkout/order data থেকে email এবং phone পাঠান। Server raw value পেলে SHA-256 hash করে দেবে।",
        ))

    if signal_rates["utm"] < 50:
        score -= 8
        issues.append(SignalIssue(
            severity="low",
            title="Campaign attribution missing",
            metric=f"{signal_rates['utm']}%",
            impact="Facebook vs TikTok campaign comparison পরিষ্কার হবে না।",
            fix="Campaign URL Builder দিয়ে ad destination URL বানিয়ে প্রতিটি campaign-এ ব্যবহার করুন।",
        ))

    for required_event in ["ViewContent", "AddToCart", "InitiateCheckout", "Purchase"]:
        if event_counts.get(required_event, 0) == 0:
            score -= 5
            issues.append(SignalIssue(
                severity="medium",
                title=f"{required_event} event not seen",
                metric="0 events",
                impact="Full funnel optimization ও diagnostics অসম্পূর্ণ থাকবে।",
                fix=f"Plugin settings-এ {required_event} enabled আছে কি না এবং site flow থেকে event fire হচ্ছে কি না test করুন।",
            ))

    if not issues:
        issues.append(SignalIssue(
            severity="ok",
            title="Signals look healthy",
            metric="All key checks passed",
            impact="Facebook/TikTok/GA4 optimization-এর জন্য current event quality ভালো।",
            fix="Campaign URL Builder ব্যবহার করে UTM discipline maintain করুন।",
        ))

    score = max(0, min(100, score))
    fb_ready = round((signal_rates["event_id"] + signal_rates["user_match"] + signal_rates["value"] + signal_rates["currency"]) / 4)
    tt_ready = round((signal_rates["event_id"] + signal_rates["user_match"] + signal_rates["content_ids"] + signal_rates["contents"]) / 4)
    ga_ready = round((signal_rates["value"] + signal_rates["currency"] + signal_rates["content_ids"] + signal_rates["utm"]) / 4)

    return SignalDoctorResponse(
        status="success",
        period_days=days,
        score=score,
        grade=_grade(score),
        total_events=total,
        platform_readiness={"facebook": fb_ready, "tiktok": tt_ready, "ga4": ga_ready},
        signal_rates=signal_rates,
        event_counts=event_counts,
        issues=issues,
    )


# ─── GET /analytics/export — CSV Export ──────────────────────────────────────

@router.get(
    "/analytics/export",
    summary="Export event logs as CSV",
)
async def analytics_export(
    client: CachedClient = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=30),
):
    """সর্বশেষ N দিনের event logs CSV হিসেবে ডাউনলোড"""
    start = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(EventLog)
        .where(and_(
            EventLog.client_id == client.id,
            EventLog.created_at >= start,
        ))
        .order_by(EventLog.created_at.desc())
        .limit(5000)
    )
    logs = result.scalars().all()

    # CSV generate
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Event Name", "Event ID", "Status", "Count", "Value", "Currency", "UTM Source", "UTM Campaign", "IP Address"])

    for log in logs:
        writer.writerow([
            log.created_at.isoformat() if log.created_at else "",
            log.event_name or "",
            log.event_id or "",
            log.status or "",
            log.event_count or 0,
            log.value or "",
            log.currency or "",
            log.utm_source or log.campaign_source or "",
            log.utm_campaign or "",
            log.ip_address or "",
        ])

    output.seek(0)
    filename = f"events_{client.name}_{days}days.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
