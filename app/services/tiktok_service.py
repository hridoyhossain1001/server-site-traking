"""TikTok Events API service."""

import logging
from typing import List

from app.schemas.event import EventData
from app.security import decrypt_token
from app.services.capi_service import get_http_client

logger = logging.getLogger(__name__)

TIKTOK_API_URL = "https://business-api.tiktok.com/open_api/v1.3/event/track/"
TIKTOK_SUPPORTED_EVENTS = {
    "AddPaymentInfo",
    "AddToCart",
    "AddToWishlist",
    "ApplicationApproval",
    "CompleteRegistration",
    "Contact",
    "CustomizeProduct",
    "Download",
    "FindLocation",
    "InitiateCheckout",
    "Purchase",
    "Schedule",
    "Search",
    "StartTrial",
    "SubmitApplication",
    "SubmitForm",
    "Subscribe",
    "ViewContent",
}


def _number(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _quantity(value) -> int:
    number = _number(value)
    if number is None:
        return 0
    return max(0, int(number))


def _extra_value(model, key):
    value = getattr(model, key, None)
    if value is not None:
        return value
    extra = getattr(model, "model_extra", None) or {}
    return extra.get(key)


def _clean_content_id(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        for item in value:
            cleaned = _clean_content_id(item)
            if cleaned:
                return cleaned
        return None
    value = str(value).strip()
    return value or None


def _first_content_id(cd, contents: list[dict] | None = None) -> str | None:
    content_id = _clean_content_id(_extra_value(cd, "content_id"))
    if content_id:
        return content_id

    if cd.content_ids:
        content_id = _clean_content_id(cd.content_ids)
        if content_id:
            return content_id

    raw_content_ids = _extra_value(cd, "content_ids")
    content_id = _clean_content_id(raw_content_ids)
    if content_id:
        return content_id

    for item in contents or []:
        content_id = _clean_content_id(item.get("content_id") or item.get("id"))
        if content_id:
            return content_id

    return None


def _map_event_name(fb_event_name: str) -> str:
    """Map Facebook event names to TikTok equivalents.
    Only maps events that are in TIKTOK_SUPPORTED_EVENTS.
    PageView is intentionally excluded — TikTok does not support it.
    """
    mapping = {
        "ViewContent": "ViewContent",
        "AddToCart": "AddToCart",
        "InitiateCheckout": "InitiateCheckout",
        "AddPaymentInfo": "AddPaymentInfo",
        "Purchase": "Purchase",
        "Lead": "SubmitForm",
        "Contact": "Contact",
        "Search": "Search",
        "Subscribe": "Subscribe",
        "CompleteRegistration": "CompleteRegistration",
    }
    return mapping.get(fb_event_name, fb_event_name)


def _normalize_tiktok_contents(cd) -> list[dict]:
    content_type = cd.content_type or "product"
    raw_contents = getattr(cd, "contents", None) or []
    normalized = []
    fallback_content_id = _first_content_id(cd)

    for item in raw_contents:
        if not isinstance(item, dict):
            continue

        content_id = item.get("content_id") or item.get("id") or fallback_content_id
        if not content_id:
            continue

        normalized_item = {
            "content_id": str(content_id),
            "content_type": item.get("content_type") or content_type,
        }

        if item.get("content_name"):
            normalized_item["content_name"] = item.get("content_name")
        if item.get("content_category"):
            normalized_item["content_category"] = item.get("content_category")

        quantity = _quantity(item.get("quantity"))
        if quantity:
            normalized_item["quantity"] = quantity

        price = _number(item.get("price"))
        if price is None:
            price = _number(item.get("item_price"))
        if price is not None:
            normalized_item["price"] = price

        normalized.append(normalized_item)

    if normalized:
        return normalized

    if cd.content_ids:
        return [
            {"content_id": str(cid), "content_type": content_type}
            for cid in cd.content_ids
            if cid
        ]

    content_id = _first_content_id(cd)
    if content_id:
        return [{"content_id": content_id, "content_type": content_type}]

    return []


def _build_properties(event: EventData) -> dict:
    if not event.custom_data:
        return {}

    cd = event.custom_data
    properties = {}

    if cd.value is not None:
        properties["value"] = cd.value
    if cd.currency:
        properties["currency"] = cd.currency
    if cd.content_type:
        properties["content_type"] = cd.content_type
    if cd.content_ids:
        properties["content_ids"] = [str(cid) for cid in cd.content_ids if cid]
        properties.setdefault("content_type", cd.content_type or "product")

    contents = _normalize_tiktok_contents(cd)
    if contents:
        properties["contents"] = contents
        first_content_id = _first_content_id(cd, contents)
        if first_content_id:
            properties["content_id"] = first_content_id
            properties.setdefault("content_ids", [first_content_id])
        total_quantity = sum(_quantity(item.get("quantity")) for item in contents)
        if total_quantity:
            properties["quantity"] = total_quantity
        if contents[0].get("content_name"):
            properties["description"] = contents[0]["content_name"]

    if cd.order_id:
        properties["order_id"] = cd.order_id
    if cd.num_items is not None:
        properties["num_items"] = cd.num_items
        properties.setdefault("quantity", cd.num_items)

    return properties


def _build_context(event: EventData) -> dict:
    context = {
        "page": {
            "url": event.event_source_url or "",
        }
    }

    if not event.user_data:
        return context

    ud = event.user_data
    if ud.client_user_agent:
        context["user_agent"] = ud.client_user_agent
    if ud.client_ip_address:
        context["ip"] = ud.client_ip_address
    if ud.ttclid:
        context["ad"] = {"callback": ud.ttclid}

    user = {}
    if ud.em:
        user["email"] = ud.em[0]
    if ud.ph:
        user["phone_number"] = ud.ph[0]
    if ud.external_id:
        user["external_id"] = ud.external_id[0]
    if ud.ttp:
        user["ttp"] = ud.ttp
    if user:
        context["user"] = user

    return context


def _build_user(event: EventData) -> dict:
    if not event.user_data:
        return {}

    ud = event.user_data
    user = {}
    if ud.em:
        user["email"] = ud.em[0]
    if ud.ph:
        user["phone"] = ud.ph[0]
    if ud.external_id:
        user["external_id"] = ud.external_id[0]
    if ud.ttp:
        user["ttp"] = ud.ttp
    if ud.ttclid:
        user["ttclid"] = ud.ttclid
    if ud.client_ip_address:
        user["ip"] = ud.client_ip_address
    if ud.client_user_agent:
        user["user_agent"] = ud.client_user_agent

    return user


def _build_tiktok_payload(client, events: List[EventData]) -> dict:
    tiktok_events = []

    for event in events:
        tt_event = {
            "event": _map_event_name(event.event_name),
            "event_id": event.event_id or "",
            "event_time": int(event.event_time),
            "page": {
                "url": event.event_source_url or "",
            },
        }

        user = _build_user(event)
        if user:
            tt_event["user"] = user

        properties = _build_properties(event)
        if properties:
            tt_event["properties"] = properties

        tiktok_events.append(tt_event)

    payload = {
        "pixel_code": client.tiktok_pixel_id,
        "event_source": "web",
        "event_source_id": client.tiktok_pixel_id,
        "data": tiktok_events,
    }

    test_event_code = getattr(client, "tiktok_test_event_code", None)
    if test_event_code:
        payload["test_event_code"] = test_event_code

    return payload


async def send_to_tiktok(client, events: List[EventData]) -> dict | None:
    """Send events to TikTok Events API."""
    if not client.tiktok_pixel_id or not client.tiktok_access_token:
        return None

    supported_events = [
        event for event in events
        if _map_event_name(event.event_name) in TIKTOK_SUPPORTED_EVENTS
    ]
    skipped_events = [
        event.event_name for event in events
        if _map_event_name(event.event_name) not in TIKTOK_SUPPORTED_EVENTS
    ]

    if not supported_events:
        logger.info(
            f"[{client.name}] TikTok: skipped unsupported event(s): "
            f"{', '.join(skipped_events)}"
        )
        return {
            "code": 0,
            "message": "No TikTok-supported events to send",
            "sent_count": 0,
            "skipped_events": skipped_events,
        }

    try:
        http_client = await get_http_client()
        headers = {
            "Access-Token": decrypt_token(client.tiktok_access_token),
            "Content-Type": "application/json",
        }

        test_event_code_used = bool(getattr(client, "tiktok_test_event_code", None))
        response = await http_client.post(
            TIKTOK_API_URL,
            json=_build_tiktok_payload(client, supported_events),
            headers=headers,
        )
        result = response.json()
        result.setdefault("sent_count", len(supported_events))
        result.setdefault("skipped_events", skipped_events)
        result["test_event_code_used"] = test_event_code_used
        response_status = response.status_code

        if response_status == 200 and result.get("code") == 0:
            logger.info(
                f"[{client.name}] TikTok: {len(supported_events)} event(s) successful. "
                f"Response: {result.get('message', 'OK')}"
            )
        else:
            logger.warning(
                f"[{client.name}] TikTok API warning: "
                f"Status={response_status}, Response={result}"
            )

        return result

    except Exception as e:
        logger.error(f"[{client.name}] TikTok error (non-fatal): {e}")
        return None
