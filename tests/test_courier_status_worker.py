import pytest

from app.services import courier_status_worker


class _Redis:
    def __init__(self, acquired):
        self.acquired = acquired
        self.set_calls = []
        self.eval_calls = []

    async def set(self, *args, **kwargs):
        self.set_calls.append((args, kwargs))
        return self.acquired

    async def eval(self, *args):
        self.eval_calls.append(args)
        return 1


@pytest.mark.asyncio
async def test_courier_poll_skips_when_another_worker_owns_lock(monkeypatch):
    redis = _Redis(acquired=False)
    ran = []
    monkeypatch.setattr(courier_status_worker, "get_redis", lambda: redis)
    monkeypatch.setattr(
        courier_status_worker,
        "_poll_active_courier_orders_unlocked",
        lambda: ran.append(True),
    )

    await courier_status_worker.poll_active_courier_orders()

    assert ran == []
    assert redis.eval_calls == []


@pytest.mark.asyncio
async def test_courier_poll_releases_owned_lock(monkeypatch):
    redis = _Redis(acquired=True)
    ran = []

    async def fake_poll():
        ran.append(True)

    monkeypatch.setattr(courier_status_worker, "get_redis", lambda: redis)
    monkeypatch.setattr(courier_status_worker, "_poll_active_courier_orders_unlocked", fake_poll)

    await courier_status_worker.poll_active_courier_orders()

    assert ran == [True]
    assert len(redis.eval_calls) == 1
