"""
Retry Service — ব্যর্থ ইভেন্ট পুনরায় Facebook-এ পাঠানোর সার্ভিস।
Background task হিসেবে চলে, exponential backoff সহ।
"""
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.client import Client
from app.models.failed_event import FailedEvent
from app.schemas.event import EventData
from app.services.capi_service import send_to_facebook

logger = logging.getLogger(__name__)

# Retry intervals (seconds): 30s, 2min, 10min, 30min, 1hr
RETRY_DELAYS = [30, 120, 600, 1800, 3600]


async def save_failed_event(
    db: AsyncSession,
    client_id: int,
    events_data: list,
    error_message: str,
) -> bool:
    """ব্যর্থ ইভেন্ট DB-তে সংরক্ষণ করো retry-এর জন্য"""
    try:
        failed = FailedEvent(
            client_id=client_id,
            event_payload=events_data,
            error_message=error_message[:500],
        )
        db.add(failed)
        await db.commit()
        logger.info(f"[Client {client_id}] Failed event saved for retry")
        return True
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to save failed event: {e}")
        return False


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _retry_is_due(failed: FailedEvent, now: datetime) -> bool:
    delay_index = min(failed.retry_count, len(RETRY_DELAYS) - 1)
    if not failed.last_retry_at:
        return True
    elapsed = (now - _as_utc(failed.last_retry_at)).total_seconds()
    return elapsed >= RETRY_DELAYS[delay_index]


async def claim_due_failed_events(db: AsyncSession, limit: int = 20) -> list[FailedEvent]:
    """
    Retry করার আগে row lock করে claim করা হয়।
    একাধিক worker থাকলেও একই failed event একসাথে পাঠানো হবে না।
    """
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(FailedEvent)
        .where(
            and_(
                FailedEvent.status.in_(["pending", "retrying"]),
                FailedEvent.retry_count < FailedEvent.max_retries,
            )
        )
        .order_by(FailedEvent.created_at.asc())
        .limit(limit)
        .with_for_update(skip_locked=True)
    )
    failed_events = result.scalars().all()

    due_events: list[FailedEvent] = []
    for failed in failed_events:
        if not _retry_is_due(failed, now):
            continue
        failed.status = "retrying"
        failed.last_retry_at = now
        due_events.append(failed)

    if due_events:
        await db.commit()
    else:
        await db.rollback()

    return due_events


async def retry_failed_events():
    """
    Background task — pending ব্যর্থ ইভেন্ট retry করে।
    প্রতি ৬০ সেকেন্ডে চলে।
    """
    while True:
        try:
            async with AsyncSessionLocal() as db:
                failed_events = await claim_due_failed_events(db)

                for failed in failed_events:
                    # Client তথ্য আনো
                    client_result = await db.execute(
                        select(Client).where(Client.id == failed.client_id)
                    )
                    client = client_result.scalar_one_or_none()
                    if not client or not client.is_active:
                        # Client inactive — dead letter queue-তে পাঠাও
                        failed.status = "dead"
                        await db.commit()
                        continue

                    try:
                        # ইভেন্ট ডাটা থেকে EventData অবজেক্ট তৈরি করো
                        events = [EventData(**e) for e in failed.event_payload]

                        # Facebook-এ পাঠাও
                        result = await send_to_facebook(client, events)

                        # সফল! স্ট্যাটাস আপডেট করো
                        failed.status = "success"
                        failed.last_retry_at = datetime.now(timezone.utc)
                        await db.commit()

                        logger.info(
                            f"[{client.name}] Retry #{failed.retry_count + 1} সফল! "
                            f"{len(events)} ইভেন্ট পাঠানো হয়েছে।"
                        )

                    except Exception as e:
                        failed.retry_count += 1
                        failed.last_retry_at = datetime.now(timezone.utc)
                        failed.status = "retrying" if failed.retry_count < failed.max_retries else "dead"
                        failed.error_message = str(e)[:500]
                        await db.commit()

                        logger.warning(
                            f"[{client.name}] Retry #{failed.retry_count} ব্যর্থ: {str(e)[:100]}"
                        )

        except Exception as e:
            logger.error(f"Retry service error: {e}")

        # ৬০ সেকেন্ড অপেক্ষা করো
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(retry_failed_events())
