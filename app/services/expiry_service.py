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

from sqlalchemy import update, and_

from app.database import AsyncSessionLocal
from app.models.pending_event import PendingEvent

logger = logging.getLogger(__name__)

EXPIRY_DAYS = 7               # Facebook-এর ৭ দিনের limit
CHECK_INTERVAL_HOURS = 1      # প্রতি ১ ঘণ্টায় চেক করো


async def expire_old_pending_events():
    """
    Background loop — প্রতি ১ ঘণ্টায় পুরোনো pending events expire করে।
    """
    logger.info("⏰ Pending Events Expiry Service শুরু হয়েছে।")

    while True:
        try:
            await asyncio.sleep(CHECK_INTERVAL_HOURS * 3600)

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
                    .returning(PendingEvent.id)
                )
                expired_ids = result.scalars().all()
                await db.commit()

                if expired_ids:
                    logger.info(
                        f"⏰ {len(expired_ids)} pending events expired "
                        f"(older than {EXPIRY_DAYS} days)"
                    )

        except Exception as e:
            logger.error(f"⏰ Expiry service error: {e}")
            await asyncio.sleep(60)  # Error হলে ১ মিনিট পরে retry
