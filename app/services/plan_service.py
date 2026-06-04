from __future__ import annotations

import math
import re
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import or_, select


TRIAL_DAYS = 14
VALID_PLAN_TIERS = {"free", "growth", "scale", "agency"}
VALID_BILLING_STATUSES = {
    "trial",
    "paid",
    "pending_payment",
    "overdue",
    "manual_invoice",
    "free",
}

FREE_EVENT_LIMIT = 5_000
TRIAL_EVENT_LIMIT = 25_000
PLAN_EVENT_LIMITS = {
    "growth": 500_000,
    "scale": 1_000_000,
    "agency": 0,
}

FREE_ORDER_LIMIT = 100
TRIAL_ORDER_LIMIT = 300
PLAN_ORDER_LIMITS = {
    "growth": 2_000,
    "scale": 10_000,
    "agency": 0,
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_plan_tier(value: str | None) -> str:
    tier = str(value or "growth").strip().lower()
    return tier if tier in VALID_PLAN_TIERS else "growth"


def normalize_billing_status(value: str | None) -> str:
    status = str(value or "paid").strip().lower()
    return status if status in VALID_BILLING_STATUSES else "paid"


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def trial_active(client, now: datetime | None = None) -> bool:
    if normalize_plan_tier(getattr(client, "plan_tier", None)) != "free":
        return False
    ends_at = _as_utc(getattr(client, "trial_ends_at", None))
    return bool(ends_at and ends_at > (now or utc_now()))


def has_growth_access(client, now: datetime | None = None) -> bool:
    tier = normalize_plan_tier(getattr(client, "plan_tier", None))
    return tier in {"growth", "scale", "agency"} or trial_active(client, now)


def effective_plan_tier(client, now: datetime | None = None) -> str:
    if trial_active(client, now):
        return "growth"
    return normalize_plan_tier(getattr(client, "plan_tier", None))


def effective_monthly_event_limit(client, now: datetime | None = None) -> int:
    if trial_active(client, now):
        return TRIAL_EVENT_LIMIT

    tier = normalize_plan_tier(getattr(client, "plan_tier", None))
    if tier == "free":
        return FREE_EVENT_LIMIT

    configured = getattr(client, "monthly_limit", None)
    if configured is not None:
        return max(0, int(configured))
    return PLAN_EVENT_LIMITS[tier]


def effective_monthly_order_limit(client, now: datetime | None = None) -> int:
    if trial_active(client, now):
        return TRIAL_ORDER_LIMIT

    tier = normalize_plan_tier(getattr(client, "plan_tier", None))
    if tier == "free":
        return FREE_ORDER_LIMIT
    return PLAN_ORDER_LIMITS[tier]


def default_monthly_event_limit(tier: str) -> int:
    normalized = normalize_plan_tier(tier)
    if normalized == "free":
        return FREE_EVENT_LIMIT
    return PLAN_EVENT_LIMITS[normalized]


def new_trial_values(now: datetime | None = None) -> dict:
    started_at = now or utc_now()
    return {
        "plan_tier": "free",
        "billing_status": "trial",
        "trial_started_at": started_at,
        "trial_ends_at": started_at + timedelta(days=TRIAL_DAYS),
        "monthly_limit": TRIAL_EVENT_LIMIT,
    }


def new_free_values() -> dict:
    return {
        "plan_tier": "free",
        "billing_status": "free",
        "trial_started_at": None,
        "trial_ends_at": None,
        "monthly_limit": FREE_EVENT_LIMIT,
    }


def trial_domains(value: str | None) -> list[str]:
    if not value:
        return []
    domains = []
    for raw_part in str(value).split(","):
        cleaned = raw_part.strip().lower()
        if not cleaned:
            continue
        cleaned = re.sub(r"^https?://", "", cleaned).split("/", 1)[0].rstrip(".")
        if cleaned.startswith("www."):
            cleaned = cleaned[4:]
        for candidate in _domain_trial_candidates(cleaned):
            if candidate and "." in candidate and len(candidate) <= 255 and candidate not in domains:
                domains.append(candidate)
    return domains


def _domain_trial_candidates(host: str) -> list[str]:
    cleaned = str(host or "").strip().lower().rstrip(".")
    if cleaned.startswith("www."):
        cleaned = cleaned[4:]
    if not cleaned or "." not in cleaned:
        return []

    labels = cleaned.split(".")
    candidates = [cleaned]
    base = _registrable_domain(labels)
    if base and base not in candidates:
        candidates.append(base)
    return candidates


def _registrable_domain(labels: list[str]) -> str | None:
    if len(labels) < 2:
        return None

    public_suffix_2 = {
        "ac.bd", "com.bd", "edu.bd", "gov.bd", "info.bd", "mil.bd",
        "net.bd", "org.bd", "sch.bd", "tv.bd",
        "co.uk", "org.uk", "ac.uk", "gov.uk",
        "com.au", "net.au", "org.au",
        "co.in", "firm.in", "gen.in", "ind.in", "net.in", "org.in",
    }
    suffix_2 = ".".join(labels[-2:])
    if suffix_2 in public_suffix_2 and len(labels) >= 3:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def trial_pixel_id(value: str | None) -> str | None:
    cleaned = str(value or "").strip()
    if not cleaned or cleaned == "0":
        return None
    return cleaned if cleaned.isdigit() else None


async def find_trial_identity_conflict(
    db,
    *,
    domain: str | None = None,
    pixel_id: str | None = None,
    exclude_client_id: int | None = None,
):
    from app.models.trial_identity import TrialIdentity

    domains = trial_domains(domain)
    pixel = trial_pixel_id(pixel_id)
    clauses = []
    if domains:
        domain_clauses = [TrialIdentity.domain.in_(domains)]
        for domain in domains:
            domain_clauses.append(TrialIdentity.domain.like(f"%.{domain}"))
        clauses.append(or_(*domain_clauses))
    if pixel:
        clauses.append(TrialIdentity.pixel_id == pixel)
    if not clauses:
        return None

    stmt = select(TrialIdentity).where(or_(*clauses))
    if exclude_client_id is not None:
        stmt = stmt.where(
            or_(
                TrialIdentity.client_id.is_(None),
                TrialIdentity.client_id != exclude_client_id,
            )
        )
    result = await db.execute(stmt.limit(1))
    return result.scalar_one_or_none()


async def require_trial_available(
    db,
    *,
    domain: str | None = None,
    pixel_id: str | None = None,
    exclude_client_id: int | None = None,
) -> None:
    conflict = await find_trial_identity_conflict(
        db,
        domain=domain,
        pixel_id=pixel_id,
        exclude_client_id=exclude_client_id,
    )
    if not conflict:
        return
    if conflict.pixel_id and trial_pixel_id(pixel_id) == conflict.pixel_id:
        detail = "This Meta Pixel ID has already used a Growth trial."
    else:
        detail = "This domain has already used a Growth trial."
    raise HTTPException(status_code=409, detail=detail)


async def record_trial_identity(
    db,
    client,
    *,
    email: str | None = None,
    source: str = "signup",
) -> int:
    from app.models.trial_identity import TrialIdentity

    created = 0
    for domain in trial_domains(getattr(client, "domain", None)):
        existing = await find_trial_identity_conflict(db, domain=domain)
        if not existing:
            db.add(
                TrialIdentity(
                    client_id=getattr(client, "id", None),
                    domain=domain,
                    email=email,
                    source=source,
                )
            )
            created += 1

    pixel = trial_pixel_id(getattr(client, "pixel_id", None))
    if pixel:
        existing = await find_trial_identity_conflict(db, pixel_id=pixel)
        if not existing:
            db.add(
                TrialIdentity(
                    client_id=getattr(client, "id", None),
                    pixel_id=pixel,
                    email=email,
                    source=source,
                )
            )
            created += 1
    return created


def assign_paid_plan(
    client,
    tier: str,
    monthly_limit: int | None = None,
    billing_status: str | None = "paid",
) -> None:
    normalized = normalize_plan_tier(tier)
    if normalized == "free":
        cancel_to_free(client)
        return
    client.plan_tier = normalized
    client.billing_status = normalize_billing_status(billing_status)
    client.trial_ends_at = None
    if monthly_limit is not None:
        client.monthly_limit = max(0, int(monthly_limit))
    else:
        client.monthly_limit = default_monthly_event_limit(normalized)


def start_growth_trial(client, now: datetime | None = None) -> None:
    for field, value in new_trial_values(now).items():
        setattr(client, field, value)


def cancel_to_free(client, now: datetime | None = None) -> None:
    client.plan_tier = "free"
    client.billing_status = "free"
    if getattr(client, "trial_ends_at", None):
        client.trial_ends_at = now or utc_now()
    _apply_free_limits(client)


def _apply_free_limits(client) -> bool:
    changed = False
    updates = {
        "enable_tiktok": False,
        "enable_ga4": False,
        "deferred_purchase": False,
        "courier_auto_send": False,
        "auto_confirm_days": 0,
        "monthly_limit": FREE_EVENT_LIMIT,
    }
    for field, value in updates.items():
        if hasattr(client, field) and getattr(client, field) != value:
            setattr(client, field, value)
            changed = True
    return changed


def apply_expired_trial_downgrade(client, now: datetime | None = None) -> bool:
    if normalize_plan_tier(getattr(client, "plan_tier", None)) != "free":
        return False
    ends_at = _as_utc(getattr(client, "trial_ends_at", None))
    if not ends_at or ends_at > (now or utc_now()):
        return False

    return _apply_free_limits(client)


def require_growth_access(client, feature_name: str) -> None:
    if not has_growth_access(client):
        raise HTTPException(
            status_code=403,
            detail=f"{feature_name} requires an active Growth trial or paid plan.",
        )


def plan_summary(client, now: datetime | None = None) -> dict:
    current = now or utc_now()
    is_trial = trial_active(client, current)
    tier = effective_plan_tier(client, current)
    labels = {
        "free": "Free Plan",
        "growth": "Growth Trial" if is_trial else "Growth Plan",
        "scale": "Scale Plan",
        "agency": "Agency Plan",
    }
    trial_ends_at = _as_utc(getattr(client, "trial_ends_at", None))
    days_remaining = 0
    if is_trial and trial_ends_at:
        days_remaining = max(1, math.ceil((trial_ends_at - current).total_seconds() / 86400))

    return {
        "tier": tier,
        "baseTier": normalize_plan_tier(getattr(client, "plan_tier", None)),
        "billingStatus": normalize_billing_status(getattr(client, "billing_status", None)),
        "name": labels[tier],
        "isTrial": is_trial,
        "trialEndsAt": trial_ends_at.isoformat() if trial_ends_at else None,
        "trialDaysRemaining": days_remaining,
        "growthFeaturesEnabled": has_growth_access(client, current),
        "eventsQuota": effective_monthly_event_limit(client, current),
        "ordersQuota": effective_monthly_order_limit(client, current),
    }


async def remaining_monthly_order_capacity(db, client_id: int, client, now: datetime | None = None) -> int | None:
    from sqlalchemy import func, select
    from app.models.pending_event import PendingEvent

    limit = effective_monthly_order_limit(client, now)
    if not limit:
        return None

    current = now or utc_now()
    month_start = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count(func.distinct(PendingEvent.order_id))).where(
            PendingEvent.client_id == client_id,
            PendingEvent.created_at >= month_start,
        )
    )
    return max(0, limit - int(result.scalar() or 0))
