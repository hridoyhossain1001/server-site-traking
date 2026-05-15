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
from sqlalchemy import select, and_, func as sql_func, extract
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

    # Conversion Funnel
    funnel_events = ["PageView", "ViewContent", "AddToCart", "InitiateCheckout", "Purchase"]
    funnel_counts = {}
    for fe in funnel_events:
        fr = await db.execute(
            select(sql_func.coalesce(sql_func.sum(EventLog.event_count), 0))
            .where(and_(
                EventLog.client_id == client.id,
                EventLog.event_name == fe,
                EventLog.status == "success",
                EventLog.created_at >= start,
            ))
        )
        funnel_counts[fe] = fr.scalar() or 0

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

    # EMQ Score — sample from recent events
    sample_r = await db.execute(
        select(EventLog.fb_response)
        .where(and_(
            EventLog.client_id == client.id,
            EventLog.status == "success",
            EventLog.created_at >= now - timedelta(hours=24),
        ))
        .limit(50)
    )
    # EMQ is estimated from available user_data fields
    emq_score = None  # Real EMQ comes from Facebook — we estimate

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
            sql_func.coalesce(sql_func.sum(EventLog.event_count), 0),
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
        .limit(10000)
    )
    logs = result.scalars().all()

    # CSV generate
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Event Name", "Event ID", "Status", "Count", "IP Address"])

    for log in logs:
        writer.writerow([
            log.created_at.isoformat() if log.created_at else "",
            log.event_name or "",
            log.event_id or "",
            log.status or "",
            log.event_count or 0,
            log.ip_address or "",
        ])

    output.seek(0)
    filename = f"events_{client.name}_{days}days.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
