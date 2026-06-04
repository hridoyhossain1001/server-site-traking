from types import SimpleNamespace

import pytest

from app.services import fast_ingest_service


class _Redis:
    def __init__(self, result):
        self.result = result
        self.calls = []

    async def eval(self, *args):
        self.calls.append(args)
        return self.result


@pytest.mark.anyio
async def test_tracker_fast_ingest_reserves_all_usage_windows_and_returns_accepted_count(monkeypatch):
    redis = _Redis(["1", "stream-id", "2"])
    monkeypatch.setattr(fast_ingest_service, "EVENT_INGEST_MODE", "redis_stream")
    monkeypatch.setattr(fast_ingest_service, "get_redis", lambda: redis)
    client = SimpleNamespace(id=7, rate_limit=10, daily_quota=20, monthly_limit=30)

    enqueued, accepted = await fast_ingest_service.dedup_reserve_usage_and_enqueue_stream(
        client,
        events_data=[
            {"event_name": "PageView", "event_id": "event-1"},
            {"event_name": "ViewContent", "event_id": "event-2"},
        ],
        request_context={"user_agent": "pytest"},
    )

    assert enqueued is True
    assert accepted == 2
    call = redis.calls[0]
    assert call[1:3] == (1, fast_ingest_service.REDIS_STREAM_KEY)
    assert any(str(value).startswith("usage:7:rate:") for value in call)
    assert any(str(value).startswith("usage:7:daily:") for value in call)
    assert any(str(value).startswith("usage:7:monthly:") for value in call)
    assert 'redis.call("DEL", unpack(dedup_keys))' in call[0]


@pytest.mark.anyio
async def test_tracker_fast_ingest_surfaces_quota_rejection(monkeypatch):
    redis = _Redis(["0", "21", "20"])
    monkeypatch.setattr(fast_ingest_service, "EVENT_INGEST_MODE", "redis_stream")
    monkeypatch.setattr(fast_ingest_service, "get_redis", lambda: redis)
    client = SimpleNamespace(id=7, rate_limit=10, daily_quota=20, monthly_limit=30)

    with pytest.raises(Exception) as exc_info:
        await fast_ingest_service.dedup_reserve_usage_and_enqueue_stream(
            client,
            events_data=[{"event_name": "PageView", "event_id": "event-1"}],
            request_context={},
        )

    assert getattr(exc_info.value, "status_code", None) == 429


@pytest.mark.anyio
async def test_tracker_fast_ingest_falls_back_when_stream_enqueue_fails(monkeypatch):
    redis = _Redis(["3", "WRONGTYPE"])
    monkeypatch.setattr(fast_ingest_service, "EVENT_INGEST_MODE", "redis_stream")
    monkeypatch.setattr(fast_ingest_service, "get_redis", lambda: redis)
    client = SimpleNamespace(id=7, rate_limit=10, daily_quota=20, monthly_limit=30)

    enqueued, accepted = await fast_ingest_service.dedup_reserve_usage_and_enqueue_stream(
        client,
        events_data=[{"event_name": "PageView", "event_id": "event-1"}],
        request_context={},
    )

    assert enqueued is False
    assert accepted == 0
    assert 'redis.pcall(' in redis.calls[0][0]


@pytest.mark.anyio
async def test_server_fast_ingest_falls_back_when_stream_enqueue_fails(monkeypatch):
    redis = _Redis(["2", "WRONGTYPE"])
    monkeypatch.setattr(fast_ingest_service, "EVENT_INGEST_MODE", "redis_stream")
    monkeypatch.setattr(fast_ingest_service, "get_redis", lambda: redis)
    client = SimpleNamespace(id=7, rate_limit=10, daily_quota=20, monthly_limit=30)

    enqueued, reserved = await fast_ingest_service.reserve_usage_and_enqueue_stream(
        client,
        events_data=[{"event_name": "PageView", "event_id": "event-1"}],
        request_context={},
    )

    assert enqueued is False
    assert reserved == {}
