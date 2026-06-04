"""
Pending Events Auto-Expiry Service
───────────────────────────────────
৭ দিনের বেশি পুরোনো pending events auto-expire করে।
Facebook ৭ দিনের বেশি পুরোনো event গ্রহণ করে না,
তাই expired events আর কোনো কাজে আসবে না।
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import update, and_, select

from app.database import AsyncSessionLocal
from app.models.pending_event import PendingEvent

logger = logging.getLogger(__name__)

EXPIRY_DAYS = 7               # Facebook-এর ৭ দিনের limit
CHECK_INTERVAL_HOURS = 1      # প্রতি ১ ঘণ্টায় চেক করো


async def downgrade_expired_trials_once(now: datetime | None = None) -> int:
    """Persist Free-plan limits for clients whose 14-day Growth trial has ended."""
    from app.models.client import Client
    from app.services.plan_service import apply_expired_trial_downgrade

    current = now or datetime.now(timezone.utc)
    async with AsyncSessionLocal() as db:
        clients_r = await db.execute(
            select(Client).where(
                and_(
                    Client.is_active == True,
                    Client.plan_tier == "free",
                    Client.trial_ends_at.is_not(None),
                    Client.trial_ends_at <= current,
                )
            )
        )
        clients = clients_r.scalars().all()
        changed_count = 0
        for client in clients:
            if apply_expired_trial_downgrade(client, current):
                changed_count += 1

        if changed_count:
            await db.commit()
            logger.info("Downgraded %s expired trial client(s) to Free limits.", changed_count)

        return changed_count


async def expire_old_pending_events():
    """
    Background loop — প্রতি ১ ঘণ্টায় পুরোনো pending events expire করে এবং expired COD orders auto-confirm করে।
    """
    logger.info("⏰ Pending Events Expiry & Auto-Confirm Service शुरू হয়েছে।")

    while True:
        try:
            await downgrade_expired_trials_once()

            # 1. Auto-confirm COD orders based on client config (older than N days)
            async with AsyncSessionLocal() as db:
                from app.models.client import Client
                from app.routers.deferred_events import _queue_confirmed_event
                from app.dependencies import _snapshot
                from app.services.plan_service import has_growth_access
                from sqlalchemy import select

                clients_r = await db.execute(
                    select(Client).where(
                        and_(
                            Client.is_active == True,
                            Client.deferred_purchase == True,
                            Client.auto_confirm_days > 0
                        )
                    )
                )
                clients = clients_r.scalars().all()

                for client in clients:
                    if not has_growth_access(client):
                        continue
                    auto_confirm_cutoff = datetime.now(timezone.utc) - timedelta(days=client.auto_confirm_days)
                    pending_r = await db.execute(
                        select(PendingEvent)
                        .where(
                            and_(
                                PendingEvent.client_id == client.id,
                                PendingEvent.status == "pending",
                                PendingEvent.created_at <= auto_confirm_cutoff
                            )
                        )
                        .with_for_update(skip_locked=True)
                    )
                    pending_events = pending_r.scalars().all()

                    if pending_events:
                        cached_client = _snapshot(client)
                        confirmed_count = 0
                        for pe in pending_events:
                            if pe.portal_state == "operations_only":
                                continue
                            try:
                                async with db.begin_nested():
                                    await _queue_confirmed_event(cached_client, pe, db)
                                    pe.status = "confirmed"
                                    pe.confirmed_at = datetime.now(timezone.utc)
                                confirmed_count += 1
                            except Exception as ex:
                                logger.error(f"⏰ Background auto-confirm failed for order {pe.order_id}: {ex}")
                        if confirmed_count:
                            await db.commit()
                            logger.info(f"⏰ Background auto-confirmed {confirmed_count} COD orders for client {client.name}")

            # 2. Expire remaining old pending events (older than 7 days)
            cutoff = datetime.now(timezone.utc) - timedelta(days=EXPIRY_DAYS)
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    update(PendingEvent)
                    .where(
                        and_(
                            PendingEvent.status == "pending",
                            PendingEvent.created_at < cutoff,
                        )
                    )
                    .values(status="expired")
                )
                expired_count = result.rowcount or 0
                await db.commit()

                if expired_count:
                    logger.info(
                        f"⏰ {expired_count} pending events expired "
                        f"(older than {EXPIRY_DAYS} days)"
                    )

            await asyncio.sleep(CHECK_INTERVAL_HOURS * 3600)

        except Exception as e:
            logger.error(f"⏰ Expiry service error: {e}")
            await asyncio.sleep(60)  # Error হলে ১ মিনিট পরে retry
