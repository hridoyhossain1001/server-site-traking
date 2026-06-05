from app.utils.event_log_helpers import build_event_log_kwargs


def test_event_log_prefers_payload_visitor_ip(monkeypatch):
    seen = {}

    def fake_geo_context(ip_address):
        seen["ip"] = ip_address
        return {
            "geo_country": "bd",
            "geo_region": "C",
            "geo_city": "Dhaka",
            "geo_district": "Dhaka",
        }

    monkeypatch.setattr("app.utils.event_log_helpers.geo_context_from_ip", fake_geo_context)

    kwargs = build_event_log_kwargs(
        client_id=1,
        event_data={
            "event_name": "PageView",
            "user_data": {
                "client_ip_address": "103.111.222.10",
                "external_id": ["a" * 64],
            },
            "custom_data": {},
        },
        status="success",
        ip_address="165.22.185.62",
    )

    assert kwargs["ip_address"] == "103.111.222.10"
    assert kwargs["visitor_key"] is not None
    assert kwargs["visitor_key"].startswith("external:")
    assert seen["ip"] == "103.111.222.10"
    assert kwargs["geo_district"] == "Dhaka"


def test_event_log_falls_back_to_request_ip_for_placeholder(monkeypatch):
    seen = {}

    def fake_geo_context(ip_address):
        seen["ip"] = ip_address
        return {
            "geo_country": None,
            "geo_region": None,
            "geo_city": None,
            "geo_district": None,
        }

    monkeypatch.setattr("app.utils.event_log_helpers.geo_context_from_ip", fake_geo_context)

    kwargs = build_event_log_kwargs(
        client_id=1,
        event_data={
            "event_name": "PageView",
            "user_data": {"client_ip_address": "8.8.8.8"},
            "custom_data": {},
        },
        status="success",
        ip_address="165.22.185.62",
    )

    assert kwargs["ip_address"] == "165.22.185.62"
    assert kwargs["visitor_key"] is None
    assert seen["ip"] == "165.22.185.62"


def test_event_log_uses_browser_cookie_for_visitor_key(monkeypatch):
    monkeypatch.setattr(
        "app.utils.event_log_helpers.geo_context_from_ip",
        lambda ip_address: {
            "geo_country": None,
            "geo_region": None,
            "geo_city": None,
            "geo_district": None,
        },
    )

    first = build_event_log_kwargs(
        client_id=1,
        event_data={
            "event_name": "PageView",
            "user_data": {"fbp": "fb.1.123.456"},
            "custom_data": {},
        },
        status="success",
        ip_address="103.111.222.10",
    )
    second = build_event_log_kwargs(
        client_id=1,
        event_data={
            "event_name": "AddToCart",
            "user_data": {"fbp": "fb.1.123.456"},
            "custom_data": {},
        },
        status="success",
        ip_address="103.111.222.10",
    )

    assert first["visitor_key"] == second["visitor_key"]
    assert first["visitor_key"].startswith("fbp:")


def test_event_log_uses_payload_user_agent_for_device_fallback(monkeypatch):
    monkeypatch.setattr(
        "app.utils.event_log_helpers.geo_context_from_ip",
        lambda ip_address: {
            "geo_country": None,
            "geo_region": None,
            "geo_city": None,
            "geo_district": None,
        },
    )

    kwargs = build_event_log_kwargs(
        client_id=1,
        event_data={
            "event_name": "PageView",
            "user_data": {
                "client_ip_address": "103.111.222.10",
                "client_user_agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
                ),
            },
            "custom_data": {
                "_bk_device_type": "unknown",
                "_bk_device_os": "Unknown",
                "_bk_device_browser": "Unknown",
            },
        },
        status="success",
        ip_address=None,
        user_agent=None,
    )

    assert kwargs["visitor_key"].startswith("net:")
    assert kwargs["device_type"] == "desktop"
    assert kwargs["device_os"] == "Windows"
    assert kwargs["device_browser"] == "Chrome"
