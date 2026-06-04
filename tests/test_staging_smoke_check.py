import pytest

from scripts.ops import staging_smoke_check


def test_build_url_handles_base_and_path_slashes():
    assert staging_smoke_check.build_url("https://api.example.com/", "/status") == "https://api.example.com/status"
    assert (
        staging_smoke_check.build_url("https://api.example.com/base", "api/v1/admin/api/summary")
        == "https://api.example.com/base/api/v1/admin/api/summary"
    )


def test_evaluate_status_rejects_degraded_by_default():
    ok, message = staging_smoke_check.evaluate_status({"status": "degraded", "db": True, "redis": False})

    assert ok is False
    assert "degraded" in message


def test_evaluate_status_can_allow_degraded_when_db_is_healthy():
    ok, message = staging_smoke_check.evaluate_status(
        {"status": "degraded", "db": True, "redis": False},
        allow_degraded=True,
    )

    assert ok is True
    assert "DB is healthy" in message


def test_evaluate_queue_rejects_critical_alerts_by_default():
    ok, message = staging_smoke_check.evaluate_queue(
        {"courier_booking_queue": {"alert_status": "critical", "queued": 0, "processing": 0, "dead": 1}}
    )

    assert ok is False
    assert "critical" in message


def test_run_smoke_calls_backend_endpoints(monkeypatch):
    calls = []
    payloads = {
        "https://api.example.com/status": {"status": "ok", "db": True, "redis": True},
        "https://api.example.com/api/v1/admin/api/summary": {
            "courier_booking_queue": {"alert_status": "healthy", "queued": 0, "processing": 0, "dead": 0}
        },
        "https://api.example.com/api/v1/admin/api/courier-booking-queue?limit=5": {
            "alert_status": "healthy",
            "queued": 0,
            "processing": 0,
            "dead": 0,
        },
    }

    def fake_fetch(url, *, headers=None, timeout=10.0):
        calls.append((url, headers, timeout))
        return 200, payloads[url]

    monkeypatch.setattr(staging_smoke_check, "fetch_json", fake_fetch)

    results = staging_smoke_check.run_smoke("https://api.example.com", "admin-key", timeout=3)

    assert all(result.ok for result in results)
    assert calls[0] == ("https://api.example.com/status", None, 3)
    assert calls[1][1] == {"X-Admin-API-Key": "admin-key"}
    assert calls[2][0].endswith("/api/v1/admin/api/courier-booking-queue?limit=5")
