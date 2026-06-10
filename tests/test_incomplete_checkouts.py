import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.dependencies import CachedClient
from app.models.incomplete_checkout import IncompleteCheckout
from app.routers.incomplete_checkouts import (
    IncompleteCheckoutConvert,
    IncompleteCheckoutUpsert,
    _normalize_phone,
    upsert_incomplete_checkout,
    convert_incomplete_checkout,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("01816101745", "8801816101745"),
        ("1816101745", "8801816101745"),
        ("+880 1816-101745", "8801816101745"),
    ],
)
def test_normalize_phone_accepts_bd_mobile_formats(raw, expected):
    assert _normalize_phone(raw) == expected


@pytest.mark.parametrize("raw", ["", "12345", "017000000000", "+12025550123"])
def test_normalize_phone_rejects_invalid_or_non_bd_numbers(raw):
    with pytest.raises(HTTPException) as exc:
        _normalize_phone(raw)
    assert exc.value.status_code == 422


def test_upsert_accepts_legacy_empty_php_campaign_array():
    payload = IncompleteCheckoutUpsert(
        visitor_id="bk.test.visitor",
        phone="01816101745",
        campaign_data=[],
    )
    assert payload.campaign_data == {}


def _cached_client() -> CachedClient:
    return CachedClient(
        id=1,
        name="Test Client",
        api_key="test-key",
        public_key="public-key",
        portal_key="portal-key",
        pixel_id="pixel",
        access_token="token",
        test_event_code=None,
        tiktok_test_event_code=None,
        is_active=True,
        domain=None,
        rate_limit=5000,
        daily_quota=100000,
        monthly_limit=50000,
        enable_facebook=True,
        enable_tiktok=True,
        enable_ga4=True,
        tiktok_pixel_id=None,
        tiktok_access_token=None,
        ga4_measurement_id=None,
        ga4_api_secret=None,
        deferred_purchase=False,
        webhook_url=None,
        plan_tier="growth",
        trial_started_at=None,
        trial_ends_at=None,
    )


@pytest.mark.asyncio
async def test_convert_marks_all_matching_open_drafts_recovered():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as db:
        payload = IncompleteCheckoutUpsert(visitor_id="bk.test.visitor", phone="01816101745")
        await upsert_incomplete_checkout(payload, _cached_client(), db)
        await upsert_incomplete_checkout(
            IncompleteCheckoutUpsert(visitor_id="bk.test.visitor.2", phone="01816101745"),
            _cached_client(),
            db,
        )

        response = await convert_incomplete_checkout(
            IncompleteCheckoutConvert(phone="01816101745", order_id="1001"),
            _cached_client(),
            db,
        )

        rows = (await db.execute(select(IncompleteCheckout))).scalars().all()

    await engine.dispose()
    assert response["converted"] is True
    assert response["converted_count"] == 2
    assert {row.status for row in rows} == {"recovered"}
    assert {row.order_id for row in rows} == {"1001"}


@pytest.mark.asyncio
async def test_upsert_after_recent_recovery_does_not_create_new_incomplete_draft():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as db:
        payload = IncompleteCheckoutUpsert(visitor_id="bk.test.visitor", phone="01816101745")
        first = await upsert_incomplete_checkout(payload, _cached_client(), db)
        await convert_incomplete_checkout(
            IncompleteCheckoutConvert(visitor_id="bk.test.visitor", phone="01816101745", order_id="1001"),
            _cached_client(),
            db,
        )
        second = await upsert_incomplete_checkout(payload, _cached_client(), db)
        count = len((await db.execute(select(IncompleteCheckout))).scalars().all())

    await engine.dispose()
    assert second["suppressed"] is True
    assert second["id"] == first["id"]
    assert second["status"] == "recovered"
    assert count == 1
