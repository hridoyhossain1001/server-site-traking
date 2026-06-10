from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

from fastapi import HTTPException
from sqlalchemy import select

from app.models.audit_log import AuditLog
from app.models.client import Client
from app.models.site_binding import SiteBinding
from app.services.plan_service import trial_domains
from app.services.redis_pool import get_redis


ACTIVE_STATUS = "active"
RELEASED_STATUSES = {"released", "transferred"}
SITE_BINDING_EVENT_TOUCH_INTERVAL_SECONDS = int(
    os.getenv("SITE_BINDING_EVENT_TOUCH_INTERVAL_SECONDS", "30")
)
SITE_BINDING_VALIDATION_CACHE_SECONDS = int(
    os.getenv("SITE_BINDING_VALIDATION_CACHE_SECONDS", "30")
)
SITE_BINDING_VALIDATION_CACHE_MAX_SIZE = int(
    os.getenv("SITE_BINDING_VALIDATION_CACHE_MAX_SIZE", "10000")
)
_SITE_BINDING_VALIDATION_CACHE: dict[str, float] = {}


def root_domain_for_site(site_host: str) -> str:
    domains = trial_domains(site_host)
    return domains[-1] if domains else str(site_host or "").strip().lower()


def host_from_url(value: str | None) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return ""
    if "://" not in raw:
        raw = "https://" + raw
    parsed = urlparse(raw)
    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def _site_conflict_error(root_domain: str) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail=(
            "This website is already connected to another Buykori workspace. "
            f"Contact Buykori support to transfer {root_domain}."
        ),
    )


def _site_forbidden_error(message: str) -> HTTPException:
    return HTTPException(status_code=403, detail=message)


def _add_site_security_event(
    db,
    *,
    action: str,
    client_id: int | None,
    ip_address: str | None = None,
    details: str = "",
) -> None:
    db.add(AuditLog(
        actor="site_binding_guard",
        action=action,
        client_id=client_id,
        ip_address=ip_address,
        details=details[:2000],
    ))


async def _should_touch_site_binding(client_id: int, root_domain: str) -> bool:
    """Throttle noisy last_event_at writes while still validating every event."""
    if SITE_BINDING_EVENT_TOUCH_INTERVAL_SECONDS <= 0:
        return True

    redis = get_redis()
    if redis is None:
        return True

    try:
        key = f"site_binding_touch:{client_id}:{root_domain}"
        return bool(
            await redis.set(
                key,
                "1",
                nx=True,
                ex=SITE_BINDING_EVENT_TOUCH_INTERVAL_SECONDS,
            )
        )
    except Exception:
        return True


def _binding_validation_cache_key(
    client_id: int,
    root_domain: str,
    installation_id: str | None,
) -> str:
    install_part = installation_id or "-"
    return f"site_binding_valid:{client_id}:{root_domain}:{install_part}"


async def _site_binding_cache_valid(
    client_id: int,
    root_domain: str,
    installation_id: str | None,
) -> bool:
    if SITE_BINDING_VALIDATION_CACHE_SECONDS <= 0:
        return False

    key = _binding_validation_cache_key(client_id, root_domain, installation_id)
    expires_at = _SITE_BINDING_VALIDATION_CACHE.get(key)
    if not expires_at:
        return False
    if expires_at <= time.monotonic():
        _SITE_BINDING_VALIDATION_CACHE.pop(key, None)
        return False
    return True


async def _mark_site_binding_cache_valid(
    client_id: int,
    root_domain: str,
    installation_id: str | None,
) -> None:
    if SITE_BINDING_VALIDATION_CACHE_SECONDS <= 0:
        return

    if len(_SITE_BINDING_VALIDATION_CACHE) >= SITE_BINDING_VALIDATION_CACHE_MAX_SIZE:
        now = time.monotonic()
        expired_keys = [
            key
            for key, expires_at in _SITE_BINDING_VALIDATION_CACHE.items()
            if expires_at <= now
        ]
        for key in expired_keys[:1000]:
            _SITE_BINDING_VALIDATION_CACHE.pop(key, None)
        if len(_SITE_BINDING_VALIDATION_CACHE) >= SITE_BINDING_VALIDATION_CACHE_MAX_SIZE:
            _SITE_BINDING_VALIDATION_CACHE.clear()

    _SITE_BINDING_VALIDATION_CACHE[
        _binding_validation_cache_key(client_id, root_domain, installation_id)
    ] = time.monotonic() + SITE_BINDING_VALIDATION_CACHE_SECONDS


async def _record_site_security_event(
    db,
    *,
    action: str,
    client_id: int | None,
    ip_address: str | None = None,
    details: str = "",
) -> None:
    _add_site_security_event(
        db,
        action=action,
        client_id=client_id,
        ip_address=ip_address,
        details=details,
    )
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise


async def _find_existing_client_domain_conflict(db, site_host: str, client_id: int):
    root_domain = root_domain_for_site(site_host)
    result = await db.execute(
        select(Client).where(
            Client.id != client_id,
            Client.is_active.is_(True),
            Client.domain.isnot(None),
        )
    )
    candidates = result.scalars().all()
    for client in candidates:
        for domain in trial_domains(client.domain):
            if root_domain_for_site(domain) == root_domain:
                return client
    return None


async def get_active_site_binding(db, site_host: str):
    root_domain = root_domain_for_site(site_host)
    result = await db.execute(
        select(SiteBinding)
        .where(
            SiteBinding.root_domain == root_domain,
            SiteBinding.status == ACTIVE_STATUS,
        )
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_site_binding(db, site_host: str, client_id: int | None = None):
    root_domain = root_domain_for_site(site_host)
    filters = [SiteBinding.root_domain == root_domain]
    if client_id is not None:
        filters.append(SiteBinding.client_id == client_id)
    result = await db.execute(
        select(SiteBinding)
        .where(*filters)
        .order_by(SiteBinding.id.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def require_site_binding_available(db, site_host: str, client_id: int) -> None:
    binding = await get_active_site_binding(db, site_host)
    if binding and int(binding.client_id) != int(client_id):
        raise _site_conflict_error(binding.root_domain)
    if binding:
        return

    existing_client = await _find_existing_client_domain_conflict(db, site_host, client_id)
    if existing_client:
        raise _site_conflict_error(root_domain_for_site(site_host))


async def upsert_active_site_binding(
    db,
    *,
    site_host: str,
    client_id: int,
    installation_id: str | None = None,
    source: str = "plugin_connect",
    now: datetime | None = None,
) -> SiteBinding:
    current = now or datetime.now(timezone.utc)
    await require_site_binding_available(db, site_host, client_id)
    root_domain = root_domain_for_site(site_host)
    binding = await get_active_site_binding(db, site_host)

    if not binding:
        binding = SiteBinding(
            client_id=client_id,
            site_host=site_host,
            root_domain=root_domain,
            installation_id=(installation_id or None),
            status=ACTIVE_STATUS,
            source=source,
            connected_at=current,
            last_seen_at=current,
        )
        db.add(binding)
    else:
        binding.site_host = site_host
        binding.last_seen_at = current
        binding.source = source
        if installation_id and not binding.installation_id:
            binding.installation_id = installation_id

    return binding


async def validate_event_site_binding(
    db,
    *,
    client,
    events: list,
    signed_site_host: str,
    installation_id: str | None = None,
    ip_address: str | None = None,
) -> None:
    site_host = host_from_url(signed_site_host)
    if not site_host:
        return

    root_domain = root_domain_for_site(site_host)
    event_hosts = []
    for event in events:
        event_host = host_from_url(getattr(event, "event_source_url", None))
        if event_host:
            event_hosts.append(event_host)
            if root_domain_for_site(event_host) != root_domain:
                await _record_site_security_event(
                    db,
                    action="site_binding.event_source_mismatch",
                    client_id=getattr(client, "id", None),
                    ip_address=ip_address,
                    details=(
                        f"signed_site={site_host}; event_source={event_host}; "
                        f"event={getattr(event, 'event_name', '')}; root={root_domain}"
                    ),
                )
                raise _site_forbidden_error("Event source URL does not match the connected website.")

    if await _site_binding_cache_valid(int(client.id), root_domain, installation_id):
        return

    binding = await get_active_site_binding(db, site_host)
    now = datetime.now(timezone.utc)
    if binding:
        if int(binding.client_id) != int(client.id):
            await _record_site_security_event(
                db,
                action="site_binding.event_wrong_workspace",
                client_id=getattr(client, "id", None),
                ip_address=ip_address,
                details=f"site={site_host}; root={root_domain}; binding_client_id={binding.client_id}",
            )
            raise _site_forbidden_error("This website is connected to a different Buykori workspace.")

        if binding.installation_id and installation_id and binding.installation_id != installation_id:
            _add_site_security_event(
                db,
                action="site_binding.installation_rebound",
                client_id=client.id,
                ip_address=ip_address,
                details=(
                    f"site={site_host}; root={root_domain}; "
                    f"previous={binding.installation_id}; received={installation_id}"
                ),
            )
            binding.installation_id = installation_id
            should_touch = True
        else:
            should_touch = False

        if installation_id and not binding.installation_id:
            binding.installation_id = installation_id
            should_touch = True
        if should_touch or await _should_touch_site_binding(int(client.id), root_domain):
            binding.site_host = site_host
            binding.last_seen_at = now
            binding.last_event_at = now
        await _mark_site_binding_cache_valid(int(client.id), root_domain, installation_id)
        return

    latest_for_client = await get_latest_site_binding(db, site_host, int(client.id))
    if latest_for_client and latest_for_client.status in RELEASED_STATUSES:
        await _record_site_security_event(
            db,
            action="site_binding.released_install_event_blocked",
            client_id=client.id,
            ip_address=ip_address,
            details=f"site={site_host}; root={root_domain}; status={latest_for_client.status}",
        )
        raise _site_forbidden_error("This website binding was released by Buykori support. Reconnect the plugin.")


async def check_site_event_rate_limit(client, site_host: str, event_count: int) -> None:
    if event_count <= 0 or not site_host:
        return
    redis = get_redis()
    if redis is None:
        return

    root_domain = root_domain_for_site(site_host)
    if not root_domain:
        return

    minute_key = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    key = f"site_usage:{getattr(client, 'id', 'unknown')}:{root_domain}:{minute_key}"
    limit = int(getattr(client, "rate_limit", None) or 5000)
    try:
        count = await redis.incrby(key, int(event_count))
        await redis.expire(key, 90)
    except Exception:
        return
    if count > limit:
        raise HTTPException(
            status_code=429,
            detail=f"Site rate limit exceeded for {root_domain}: {count}/{limit} events/min.",
        )


async def release_site_binding(
    db,
    *,
    binding_id: int,
    actor: str,
    reason: str,
    now: datetime | None = None,
) -> SiteBinding:
    binding = await db.get(SiteBinding, binding_id)
    if not binding:
        raise HTTPException(status_code=404, detail="Site binding not found.")
    current = now or datetime.now(timezone.utc)
    binding.status = "released"
    binding.released_at = current
    binding.released_by = actor
    binding.release_reason = reason
    return binding


async def transfer_site_binding(
    db,
    *,
    site_host: str,
    target_client_id: int,
    actor: str,
    reason: str,
    now: datetime | None = None,
) -> SiteBinding:
    current = now or datetime.now(timezone.utc)
    binding = await get_active_site_binding(db, site_host)
    if not binding:
        raise HTTPException(status_code=404, detail="Active site binding not found.")
    if int(binding.client_id) == int(target_client_id):
        return binding

    target = await db.get(Client, target_client_id)
    if not target or not target.is_active:
        raise HTTPException(status_code=404, detail="Target client not found or inactive.")

    original_site_host = binding.site_host
    root_domain = binding.root_domain
    installation_id = binding.installation_id
    binding.status = "transferred"
    binding.released_at = current
    binding.released_by = actor
    binding.release_reason = reason
    await db.flush()

    new_binding = SiteBinding(
        client_id=target_client_id,
        site_host=original_site_host,
        root_domain=root_domain,
        installation_id=installation_id,
        status=ACTIVE_STATUS,
        source="admin_transfer",
        connected_at=current,
        last_seen_at=current,
    )
    db.add(new_binding)
    return new_binding
