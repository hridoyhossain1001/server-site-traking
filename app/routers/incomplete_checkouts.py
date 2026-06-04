import hashlib
import re
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CachedClient, get_current_client
from app.models.incomplete_checkout import IncompleteCheckout
from app.services.plan_service import require_growth_access


router = APIRouter()


class IncompleteCheckoutUpsert(BaseModel):
    visitor_id: str = Field(min_length=8, max_length=255)
    phone: str = Field(min_length=8, max_length=32)
    customer_name: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=500)
    products: list[dict] = Field(default_factory=list, max_length=30)
    amount: Decimal = Field(default=Decimal("0"), ge=0, le=100000000)
    currency: str = Field(default="BDT", min_length=3, max_length=8)
    page_url: str | None = Field(default=None, max_length=1000)
    campaign_data: dict = Field(default_factory=dict)

    @field_validator("campaign_data", mode="before")
    @classmethod
    def normalize_empty_campaign_data(cls, value):
        # PHP json_encode serializes an empty associative array as [] unless
        # explicitly cast to object. Accept that legacy relay shape as empty.
        return {} if value == [] or value is None else value


class IncompleteCheckoutConvert(BaseModel):
    visitor_id: str | None = Field(default=None, max_length=255)
    phone: str = Field(min_length=8, max_length=32)
    order_id: str = Field(min_length=1, max_length=255)


def _normalize_phone(value: str) -> str:
    digits = re.sub(r"\D+", "", value or "")
    if len(digits) == 11 and digits.startswith("01"):
        return "88" + digits
    if len(digits) == 10 and digits.startswith("1"):
        return "880" + digits
    if len(digits) == 13 and digits.startswith("8801"):
        return digits
    raise HTTPException(status_code=422, detail="A valid Bangladesh mobile number is required.")


def _phone_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@router.post("/incomplete-checkouts/upsert")
async def upsert_incomplete_checkout(
    payload: IncompleteCheckoutUpsert,
    client: CachedClient = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
):
    require_growth_access(client, "Incomplete checkout recovery")
    phone = _normalize_phone(payload.phone)
    phone_hash = _phone_hash(phone)
    visitor_id = payload.visitor_id.strip()
    result = await db.execute(
        select(IncompleteCheckout)
        .where(
            IncompleteCheckout.client_id == client.id,
            IncompleteCheckout.visitor_id == visitor_id,
            IncompleteCheckout.phone_hash == phone_hash,
            IncompleteCheckout.status.in_(["active", "incomplete", "contacted"]),
        )
        .order_by(desc(IncompleteCheckout.id))
        .limit(1)
    )
    draft = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if not draft:
        draft = IncompleteCheckout(client_id=client.id, visitor_id=visitor_id, phone=phone, phone_hash=phone_hash)
        db.add(draft)

    draft.customer_name = (payload.customer_name or "").strip() or None
    draft.email = (payload.email or "").strip() or None
    draft.address = (payload.address or "").strip() or None
    draft.products = payload.products[:30]
    draft.amount = payload.amount
    draft.currency = payload.currency.strip().upper()
    draft.page_url = (payload.page_url or "").strip() or None
    draft.campaign_data = payload.campaign_data
    draft.last_activity_at = now
    if draft.status == "incomplete":
        draft.status = "active"
    await db.commit()
    await db.refresh(draft)
    return {"success": True, "id": draft.id, "status": draft.status}


@router.post("/incomplete-checkouts/convert")
async def convert_incomplete_checkout(
    payload: IncompleteCheckoutConvert,
    client: CachedClient = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
):
    phone_hash = _phone_hash(_normalize_phone(payload.phone))
    clauses = [
        IncompleteCheckout.client_id == client.id,
        IncompleteCheckout.phone_hash == phone_hash,
        IncompleteCheckout.status.in_(["active", "incomplete", "contacted"]),
    ]
    if payload.visitor_id:
        clauses.append(IncompleteCheckout.visitor_id == payload.visitor_id.strip())
    result = await db.execute(
        select(IncompleteCheckout).where(and_(*clauses)).order_by(desc(IncompleteCheckout.last_activity_at)).limit(1)
    )
    draft = result.scalar_one_or_none()
    if not draft:
        return {"success": True, "converted": False}
    draft.status = "recovered"
    draft.order_id = payload.order_id.strip()
    draft.converted_at = datetime.now(timezone.utc)
    draft.last_activity_at = draft.converted_at
    await db.commit()
    return {"success": True, "converted": True, "id": draft.id}
