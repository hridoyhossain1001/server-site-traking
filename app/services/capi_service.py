import httpx
import logging
from typing import List
from app.models.client import Client
from app.schemas.event import EventData
from app.security import decrypt_token

logger = logging.getLogger(__name__)

FACEBOOK_API_VERSION = "v20.0"


async def send_to_facebook(client: Client, events: List[EventData]) -> dict:
    """
    ক্লায়েন্টের Pixel ID ও Access Token ব্যবহার করে
    Facebook CAPI-তে ইভেন্ট পাঠায়।
    """
    url = (
        f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"
        f"/{client.pixel_id}/events"
    )

    # ইভেন্ট ডাটা প্রস্তুত করা
    events_data = [event.model_dump(exclude_none=True) for event in events]

    payload = {
        "data": events_data,
        "access_token": decrypt_token(client.access_token),  # 🔐 Decrypt before sending
    }

    # Test Event Code থাকলে যোগ করো (FB Events Manager-এ টেস্ট করার সময়)
    if client.test_event_code:
        payload["test_event_code"] = client.test_event_code

    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            response = await http_client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info(
                f"[{client.name}] {len(events)} ইভেন্ট পাঠানো সফল। "
                f"FB Response: {result}"
            )
            return result

    except httpx.HTTPStatusError as e:
        logger.error(
            f"[{client.name}] Facebook API Error: {e.response.status_code} - {e.response.text}"
        )
        raise

    except httpx.RequestError as e:
        logger.error(f"[{client.name}] Network Error: {str(e)}")
        raise
