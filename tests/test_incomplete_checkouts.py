import pytest
from fastapi import HTTPException

from app.routers.incomplete_checkouts import IncompleteCheckoutUpsert, _normalize_phone


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
