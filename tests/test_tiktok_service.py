import os
from types import SimpleNamespace

os.environ.setdefault("ADMIN_PASSWORD", "pbkdf2_sha256$210000$dGVzdC1hZG1pbi1zYWx0LTE=$9gwSQUsI_uzxaNpdvx_cOcpF4opgO7Ma_Hcmq3z4kSU=")
os.environ.setdefault("ADMIN_API_KEY", "test-admin-api-key")
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")
os.environ.setdefault("ENCRYPTION_KEY", "ZFhnf1szwemka8kBbH9jPTC7oKBRTEv0EqWt1J8AD0M=")

from app.schemas.event import EventData
from app.services.tiktok_service import _build_tiktok_payload, _map_event_name


def test_tiktok_pageview_does_not_become_viewcontent():
    assert _map_event_name("PageView") == "PageView"


def test_tiktok_purchase_uses_current_standard_event_name():
    assert _map_event_name("Purchase") == "Purchase"


def test_tiktok_viewcontent_keeps_product_content_ids():
    client = SimpleNamespace(tiktok_pixel_id="TT_PIXEL", tiktok_test_event_code=None)
    event = EventData(
        event_name="ViewContent",
        event_time=1710000000,
        event_id="view-123",
        event_source_url="https://example.com/product/123",
        custom_data={
            "content_ids": ["123"],
            "content_type": "product",
            "value": 1200,
            "currency": "BDT",
        },
    )

    payload = _build_tiktok_payload(client, [event])

    assert payload["data"][0]["event"] == "ViewContent"
    assert payload["data"][0]["properties"]["content_ids"] == ["123"]
    assert payload["data"][0]["properties"]["content_id"] == "123"
    assert payload["data"][0]["properties"]["content_type"] == "product"
    assert payload["data"][0]["properties"]["contents"] == [
        {"content_id": "123", "content_type": "product"}
    ]


def test_tiktok_test_code_uses_events_api_payload_shape():
    client = SimpleNamespace(tiktok_pixel_id="TT_PIXEL", tiktok_test_event_code="TEST123")
    event = EventData(
        event_name="InitiateCheckout",
        event_time=1710000000,
        event_id="checkout-123",
        event_source_url="https://example.com/checkout",
        custom_data={
            "content_ids": ["123"],
            "content_type": "product",
            "value": 1200,
            "currency": "BDT",
        },
    )

    payload = _build_tiktok_payload(client, [event])

    assert payload["event_source"] == "web"
    assert payload["test_event_code"] == "TEST123"
    assert payload["data"][0]["event"] == "InitiateCheckout"
    assert payload["data"][0]["event_time"] == 1710000000
    assert "timestamp" not in payload["data"][0]


def test_tiktok_payload_includes_ttp_and_ttclid():
    client = SimpleNamespace(tiktok_pixel_id="TT_PIXEL", tiktok_test_event_code=None)
    event = EventData(
        event_name="PageView",
        event_time=1710000000,
        event_id="page-123",
        event_source_url="https://example.com/?ttclid=click-123",
        user_data={
            "client_user_agent": "Mozilla/5.0",
            "client_ip_address": "203.0.113.10",
            "ttp": "ttp-cookie",
            "ttclid": "click-123",
        },
    )

    payload = _build_tiktok_payload(client, [event])
    user = payload["data"][0]["user"]

    assert user["ttp"] == "ttp-cookie"
    assert user["ttclid"] == "click-123"
    assert user["ip"] == "203.0.113.10"
    assert user["user_agent"] == "Mozilla/5.0"


def test_tiktok_payload_uses_direct_user_identifiers():
    client = SimpleNamespace(tiktok_pixel_id="TT_PIXEL", tiktok_test_event_code=None)
    event = EventData(
        event_name="InitiateCheckout",
        event_time=1710000000,
        event_id="checkout-identity",
        event_source_url="https://example.com/checkout",
        user_data={
            "em": ["a" * 64],
            "ph": ["b" * 64],
            "external_id": ["c" * 64],
            "client_user_agent": "Mozilla/5.0",
            "client_ip_address": "203.0.113.10",
        },
    )

    payload = _build_tiktok_payload(client, [event])
    event_payload = payload["data"][0]

    assert "context" not in event_payload
    assert event_payload["user"] == {
        "email": "a" * 64,
        "phone": "b" * 64,
        "external_id": "c" * 64,
        "ip": "203.0.113.10",
        "user_agent": "Mozilla/5.0",
    }


def test_tiktok_purchase_normalizes_fb_contents_shape():
    client = SimpleNamespace(tiktok_pixel_id="TT_PIXEL", tiktok_test_event_code=None)
    event = EventData(
        event_name="Purchase",
        event_time=1710000000,
        event_id="purchase-123",
        event_source_url="https://example.com/checkout/order-received/123",
        custom_data={
            "content_ids": ["123"],
            "content_type": "product",
            "value": 1200,
            "currency": "BDT",
            "contents": [
                {
                    "id": "123",
                    "content_name": "Test Product",
                    "content_category": "Shoes",
                    "quantity": 2,
                    "item_price": 600,
                }
            ],
        },
    )

    payload = _build_tiktok_payload(client, [event])

    assert payload["data"][0]["event"] == "Purchase"
    assert payload["data"][0]["properties"]["content_ids"] == ["123"]
    assert payload["data"][0]["properties"]["contents"] == [
        {
            "content_id": "123",
            "content_type": "product",
            "content_name": "Test Product",
            "content_category": "Shoes",
            "quantity": 2,
            "price": 600,
        }
    ]
