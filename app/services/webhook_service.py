"""
Webhook Service — Custom outbound webhook sender.
প্রতিটি event fire হলে ক্লায়েন্টের webhook_url-এ data forward করে।
"""

import logging
from datetime import datetime, timezone

from app.services.capi_service import get_http_client

logger = logging.getLogger(__name__)


async def send_webhook(webhook_url: str, event_type: str, data: dict) -> bool:
    """Custom webhook URL-এ event data পাঠায়। Shared HTTP client ব্যবহার করে।"""
    if not webhook_url:
        return False

    payload = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
        "source": "capi_gateway",
    }

    try:
        http_client = await get_http_client()
        resp = await http_client.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10.0,
        )
        logger.info(f"🔗 Webhook sent to {webhook_url[:40]}... status={resp.status_code}")
        return resp.status_code < 400
    except Exception as e:
        logger.error(f"🔗 Webhook send error: {e}")
        return False
