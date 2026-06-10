from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.site_binding_service import (
    require_site_binding_available,
    root_domain_for_site,
    upsert_active_site_binding,
    validate_event_site_binding,
)


class _Result:
    def __init__(self, scalar=None, rows=None):
        self.scalar = scalar
        self.rows = rows or []

    def scalar_one_or_none(self):
        return self.scalar

    def scalars(self):
        return self

    def all(self):
        return self.rows


class _Db:
    def __init__(self, *results):
        self.results = list(results)
        self.added = []

    async def execute(self, _stmt):
        if not self.results:
            return _Result()
        return self.results.pop(0)

    def add(self, row):
        self.added.append(row)

    async def commit(self):
        return None

    async def rollback(self):
        return None


def test_root_domain_for_site_uses_main_domain_for_subdomains():
    assert root_domain_for_site("checkout.example.com") == "example.com"
    assert root_domain_for_site("shop.example.com.bd") == "example.com.bd"


@pytest.mark.anyio
async def test_site_binding_allows_same_client():
    db = _Db(_Result(SimpleNamespace(client_id=7, root_domain="example.com")))

    await require_site_binding_available(db, "checkout.example.com", 7)


@pytest.mark.anyio
async def test_site_binding_blocks_other_active_binding():
    db = _Db(_Result(SimpleNamespace(client_id=8, root_domain="example.com")))

    with pytest.raises(HTTPException) as exc:
        await require_site_binding_available(db, "checkout.example.com", 7)

    assert exc.value.status_code == 409
    assert "already connected" in exc.value.detail


@pytest.mark.anyio
async def test_site_binding_blocks_existing_client_domain_conflict():
    db = _Db(
        _Result(None),
        _Result(rows=[SimpleNamespace(id=8, domain="shop.example.com.bd")]),
    )

    with pytest.raises(HTTPException) as exc:
        await require_site_binding_available(db, "checkout.example.com.bd", 7)

    assert exc.value.status_code == 409
    assert "example.com.bd" in exc.value.detail


@pytest.mark.anyio
async def test_upsert_active_site_binding_creates_root_domain_binding():
    db = _Db(
        _Result(None),
        _Result(rows=[]),
        _Result(None),
    )

    binding = await upsert_active_site_binding(
        db,
        site_host="checkout.example.com",
        client_id=7,
        source="test",
    )

    assert len(db.added) == 1
    assert binding.client_id == 7
    assert binding.site_host == "checkout.example.com"
    assert binding.root_domain == "example.com"
    assert binding.status == "active"


@pytest.mark.anyio
async def test_event_site_binding_updates_active_same_installation():
    binding = SimpleNamespace(
        id=1,
        client_id=7,
        root_domain="example.com",
        installation_id="install-1",
        site_host="checkout.example.com",
        last_seen_at=None,
        last_event_at=None,
    )
    db = _Db(_Result(binding))
    event = SimpleNamespace(event_name="PageView", event_source_url="https://checkout.example.com/offer")
    client = SimpleNamespace(id=7)

    await validate_event_site_binding(
        db,
        client=client,
        events=[event],
        signed_site_host="checkout.example.com",
        installation_id="install-1",
    )

    assert binding.last_event_at is not None
    assert binding.site_host == "checkout.example.com"


@pytest.mark.anyio
async def test_event_site_binding_throttles_repeated_timestamp_writes(monkeypatch):
    class RedisThrottle:
        async def set(self, *_args, **_kwargs):
            return False

    binding = SimpleNamespace(
        id=1,
        client_id=7,
        root_domain="example.com",
        installation_id="install-1",
        site_host="checkout.example.com",
        last_seen_at=None,
        last_event_at=None,
    )
    db = _Db(_Result(binding))
    event = SimpleNamespace(event_name="PageView", event_source_url="https://checkout.example.com/offer")
    client = SimpleNamespace(id=7)
    monkeypatch.setattr("app.services.site_binding_service.get_redis", lambda: RedisThrottle())

    await validate_event_site_binding(
        db,
        client=client,
        events=[event],
        signed_site_host="checkout.example.com",
        installation_id="install-1",
    )

    assert binding.last_event_at is None
    assert binding.last_seen_at is None


@pytest.mark.anyio
async def test_event_site_binding_cache_hit_skips_active_binding_lookup():
    from app.services import site_binding_service

    site_binding_service._SITE_BINDING_VALIDATION_CACHE.clear()
    binding = SimpleNamespace(
        id=1,
        client_id=7,
        root_domain="example.com",
        installation_id="install-1",
        site_host="checkout.example.com",
        last_seen_at=None,
        last_event_at=None,
    )
    event = SimpleNamespace(event_name="PageView", event_source_url="https://checkout.example.com/offer")
    client = SimpleNamespace(id=7)

    await validate_event_site_binding(
        _Db(_Result(binding)),
        client=client,
        events=[event],
        signed_site_host="checkout.example.com",
        installation_id="install-1",
    )

    db = _Db()
    await validate_event_site_binding(
        db,
        client=client,
        events=[event],
        signed_site_host="checkout.example.com",
        installation_id="install-1",
    )

    assert db.results == []
    site_binding_service._SITE_BINDING_VALIDATION_CACHE.clear()


@pytest.mark.anyio
async def test_event_site_binding_rebinds_same_domain_installation_mismatch():
    binding = SimpleNamespace(
        id=1,
        client_id=7,
        root_domain="example.com",
        installation_id="install-1",
        site_host="checkout.example.com",
    )
    db = _Db(_Result(binding))
    event = SimpleNamespace(event_name="PageView", event_source_url="https://checkout.example.com/offer")
    client = SimpleNamespace(id=7)

    await validate_event_site_binding(
        db,
        client=client,
        events=[event],
        signed_site_host="checkout.example.com",
        installation_id="install-2",
    )

    assert binding.installation_id == "install-2"
    assert binding.last_event_at is not None
    assert len(db.added) == 1
    assert db.added[0].action == "site_binding.installation_rebound"


@pytest.mark.anyio
async def test_event_site_binding_blocks_released_binding():
    released = SimpleNamespace(
        id=1,
        client_id=7,
        root_domain="example.com",
        status="released",
    )
    db = _Db(_Result(None), _Result(released))
    event = SimpleNamespace(event_name="PageView", event_source_url="https://checkout.example.com/offer")
    client = SimpleNamespace(id=7)

    with pytest.raises(HTTPException) as exc:
        await validate_event_site_binding(
            db,
            client=client,
            events=[event],
            signed_site_host="checkout.example.com",
            installation_id="install-1",
        )

    assert exc.value.status_code == 403
    assert "released" in exc.value.detail.lower()
