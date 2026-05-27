import logging
import uuid
from typing import Dict, Any, List

from app.services.capi_service import get_http_client
from app.security import decrypt_token

logger = logging.getLogger(__name__)


def extract_ga4_client_id(cookies: dict) -> str:
    """Extract client_id from _ga cookie or generate a random one."""
    ga_cookie = cookies.get("_ga")
    if ga_cookie:
        # Example _ga cookie format: GA1.1.123456789.123456789
        parts = ga_cookie.split('.')
        if len(parts) >= 4:
            return f"{parts[-2]}.{parts[-1]}"

    # Fallback to a random UUID if not found
    return str(uuid.uuid4())

def map_event_to_ga4(event_name: str) -> str:
    """Map Facebook standard events to GA4 standard events."""
    mapping = {
        "PageView": "page_view",
        "ViewContent": "view_item",
        "Search": "search",
        "AddToCart": "add_to_cart",
        "InitiateCheckout": "begin_checkout",
        "AddPaymentInfo": "add_payment_info",
        "Purchase": "purchase",
        "Lead": "generate_lead",
        "CompleteRegistration": "sign_up",
        "Contact": "contact",
    }
    return mapping.get(event_name, event_name.lower().replace(' ', '_'))


def _ga4_items(custom_data: Dict[str, Any]) -> list[dict]:
    items = []
    raw_contents = custom_data.get("contents") or []
    for item in raw_contents:
        if not isinstance(item, dict):
            continue
        item_id = item.get("content_id") or item.get("id") or item.get("item_id")
        if not item_id:
            continue
        ga_item = {"item_id": str(item_id)}
        if item.get("content_name"):
            ga_item["item_name"] = item["content_name"]
        if item.get("content_category"):
            ga_item["item_category"] = item["content_category"]
        if item.get("quantity") is not None:
            ga_item["quantity"] = item["quantity"]
        if item.get("price") is not None:
            ga_item["price"] = item["price"]
        elif item.get("item_price") is not None:
            ga_item["price"] = item["item_price"]
        items.append(ga_item)

    if items:
        return items

    return [{"item_id": str(item_id)} for item_id in custom_data.get("content_ids") or [] if item_id]


async def send_to_ga4(events: List[Dict[str, Any]], measurement_id: str, api_secret: str, cookies: dict, ip_address: str, user_agent: str):
    """
    Send events to GA4 via Measurement Protocol.
    Uses the shared persistent HTTP client from capi_service.
    """
    if not measurement_id or not api_secret:
        return

    decrypted_secret = decrypt_token(api_secret)
    url = f"https://www.google-analytics.com/mp/collect?measurement_id={measurement_id}&api_secret={decrypted_secret}"

    # Extract client_id (try first event's custom_data or cookies, then fallback to uuid)
    client_id = None
    if events:
        first_evt_cd = events[0].get("custom_data") or {}
        raw_ga = first_evt_cd.get("_ga") or first_evt_cd.get("client_id") or events[0].get("_ga") or events[0].get("client_id")
        if raw_ga:
            if isinstance(raw_ga, str) and "." in raw_ga:
                parts = raw_ga.split('.')
                if len(parts) >= 4:
                    client_id = f"{parts[-2]}.{parts[-1]}"
                else:
                    client_id = raw_ga
            else:
                client_id = str(raw_ga)

    if not client_id:
        client_id = extract_ga4_client_id(cookies)

    user_properties = {}
    ga4_events = []

    for evt in events:
        fb_event_name = evt.get("event_name", "")
        ga4_event_name = map_event_to_ga4(fb_event_name)

        # Build GA4 parameters
        params = {}

        # Add basic info
        if evt.get("event_source_url"):
            params["page_location"] = evt.get("event_source_url")

        custom_data = evt.get("custom_data", {})
        if custom_data:
            if "value" in custom_data:
                try:
                    params["value"] = float(custom_data["value"])
                except (TypeError, ValueError):
                    pass
            if "currency" in custom_data:
                params["currency"] = custom_data["currency"]
            items = _ga4_items(custom_data)
            if items:
                params["items"] = items
            for utm_key in ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"]:
                if custom_data.get(utm_key):
                    params[utm_key] = custom_data[utm_key]

            # Extract GA4 Session ID from custom_data or root-level event keys
            session_id = custom_data.get("session_id") or custom_data.get("ga_session_id") or evt.get("session_id") or evt.get("ga_session_id")
            if session_id:
                params["session_id"] = str(session_id)
                # Prevent session attribution loss (not set) by marking as actively engaged
                params["engagement_time_msec"] = 100

        # NOTE: user_data fields (ct, country, etc.) are SHA-256 hashed by this point
        # and cannot be used as meaningful GA4 user properties. GeoIP data should be
        # set separately if raw location is needed for GA4.

        # Optional: transaction_id for Purchase
        if ga4_event_name == "purchase":
            order_id = custom_data.get("order_id") or evt.get("event_id")
            if order_id:
                params["transaction_id"] = order_id

        ga4_event = {
            "name": ga4_event_name,
            "params": params
        }
        ga4_events.append(ga4_event)

    if not ga4_events:
        return

    payload = {
        "client_id": client_id,
        "events": ga4_events
    }

    if events:
        event_time = events[0].get("event_time")
        if event_time:
            try:
                payload["timestamp_micros"] = int(event_time) * 1000000
            except (ValueError, TypeError):
                pass
    if user_properties:
        payload["user_properties"] = user_properties

    try:
        http_client = await get_http_client()
        response = await http_client.post(url, json=payload)
        # GA4 Measurement Protocol always returns 2xx even if invalid, unless request is malformed
        if response.status_code >= 400:
            logger.error(f"GA4 error: {response.text}")
            return {"ok": False, "status_code": response.status_code, "error": response.text[:500]}
        return {"ok": True, "status_code": response.status_code}
    except Exception as e:
        logger.error(f"Failed to send to GA4: {e}")
        return {"ok": False, "error": str(e)}
