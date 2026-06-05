import re
from typing import Any

from app.services.geoip_service import get_location_data


BD_DISTRICT_ALIASES = {
    "bagerhat": "Bagerhat",
    "bandarban": "Bandarban",
    "barguna": "Barguna",
    "barisal": "Barisal",
    "barishal": "Barisal",
    "bhola": "Bhola",
    "bogra": "Bogura",
    "bogura": "Bogura",
    "brahmanbaria": "Brahmanbaria",
    "chandpur": "Chandpur",
    "chapainawabganj": "Chapainawabganj",
    "chapa nawabganj": "Chapainawabganj",
    "nawabganj": "Chapainawabganj",
    "chattogram": "Chattogram",
    "chittagong": "Chattogram",
    "chuadanga": "Chuadanga",
    "comilla": "Cumilla",
    "cumilla": "Cumilla",
    "coxs bazar": "Cox's Bazar",
    "cox bazar": "Cox's Bazar",
    "dhaka": "Dhaka",
    "dacca": "Dhaka",
    "dinajpur": "Dinajpur",
    "faridpur": "Faridpur",
    "feni": "Feni",
    "gaibandha": "Gaibandha",
    "gazipur": "Gazipur",
    "gopalganj": "Gopalganj",
    "habiganj": "Habiganj",
    "jamalpur": "Jamalpur",
    "jashore": "Jashore",
    "jessore": "Jashore",
    "jhalokati": "Jhalokati",
    "jhalkathi": "Jhalokati",
    "jhenaidah": "Jhenaidah",
    "joypurhat": "Joypurhat",
    "khagrachhari": "Khagrachhari",
    "khagrachari": "Khagrachhari",
    "khulna": "Khulna",
    "kishoreganj": "Kishoreganj",
    "kurigram": "Kurigram",
    "kushtia": "Kushtia",
    "lakshmipur": "Lakshmipur",
    "laxmipur": "Lakshmipur",
    "lalmonirhat": "Lalmonirhat",
    "madaripur": "Madaripur",
    "magura": "Magura",
    "manikganj": "Manikganj",
    "meherpur": "Meherpur",
    "moulvibazar": "Moulvibazar",
    "maulvibazar": "Moulvibazar",
    "munshiganj": "Munshiganj",
    "mymensingh": "Mymensingh",
    "naogaon": "Naogaon",
    "narail": "Narail",
    "narayanganj": "Narayanganj",
    "narsingdi": "Narsingdi",
    "natore": "Natore",
    "netrokona": "Netrokona",
    "netrakona": "Netrokona",
    "nilphamari": "Nilphamari",
    "noakhali": "Noakhali",
    "pabna": "Pabna",
    "panchagarh": "Panchagarh",
    "patuakhali": "Patuakhali",
    "pirojpur": "Pirojpur",
    "rajbari": "Rajbari",
    "rajshahi": "Rajshahi",
    "rangamati": "Rangamati",
    "rangpur": "Rangpur",
    "satkhira": "Satkhira",
    "shariatpur": "Shariatpur",
    "sherpur": "Sherpur",
    "sirajganj": "Sirajganj",
    "sunamganj": "Sunamganj",
    "sylhet": "Sylhet",
    "tangail": "Tangail",
    "thakurgaon": "Thakurgaon",
}


def _clean_key(value: Any) -> str:
    if value is None:
        return ""
    value = str(value).strip().lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def normalize_bd_district(*values: Any) -> str | None:
    for value in values:
        key = _clean_key(value)
        if not key:
            continue
        if key in BD_DISTRICT_ALIASES:
            return BD_DISTRICT_ALIASES[key]
        for alias, district in BD_DISTRICT_ALIASES.items():
            if alias in key:
                return district
    return None


def _text(value: Any, max_len: int = 80) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    return value[:max_len] if value else None


def _int_or_none(value: Any) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    if number <= 0 or number > 10000:
        return None
    return number


def _device_type(value: Any) -> str | None:
    key = _clean_key(value)
    if not key or key in {"unknown", "not set", "n a", "na", "none", "null"}:
        return None
    if key in {"mobile", "phone", "smartphone"}:
        return "mobile"
    if key in {"tablet", "tab"}:
        return "tablet"
    if key in {"pc", "desktop", "laptop", "computer"}:
        return "desktop"
    return key[:24]


def parse_user_agent(user_agent: str | None) -> dict:
    ua = user_agent or ""
    lower = ua.lower()

    if "edg/" in lower or "edgios" in lower:
        browser = "Edge"
    elif "opr/" in lower or "opera" in lower:
        browser = "Opera"
    elif "samsungbrowser" in lower:
        browser = "Samsung Internet"
    elif "firefox" in lower or "fxios" in lower:
        browser = "Firefox"
    elif "crios" in lower or "chrome" in lower:
        browser = "Chrome"
    elif "safari" in lower:
        browser = "Safari"
    else:
        browser = "Unknown"

    if "android" in lower:
        os_name = "Android"
    elif "iphone" in lower or "ipad" in lower or "ipod" in lower:
        os_name = "iOS"
    elif "windows" in lower:
        os_name = "Windows"
    elif "mac os" in lower or "macintosh" in lower:
        os_name = "macOS"
    elif "linux" in lower:
        os_name = "Linux"
    else:
        os_name = "Unknown"

    if "ipad" in lower or "tablet" in lower:
        device_type = "tablet"
    elif "mobile" in lower or "iphone" in lower or ("android" in lower and "mobile" in lower):
        device_type = "mobile"
    else:
        device_type = "desktop"

    return {
        "device_type": device_type,
        "device_os": os_name,
        "device_browser": browser,
    }


def extract_device_metadata(
    custom_data: dict | None = None,
    user_agent: str | None = None,
    context_device: dict | None = None,
) -> dict:
    custom_data = custom_data or {}
    context_device = context_device or {}
    parsed = parse_user_agent(user_agent)

    def _known_text(*values: Any) -> str | None:
        for value in values:
            text = _text(value, 40)
            if text and text.strip().lower() not in {"unknown", "not set", "n/a", "na", "none", "null"}:
                return text
        return None

    def _known_device_type(*values: Any) -> str | None:
        for value in values:
            device_type = _device_type(value)
            if device_type:
                return device_type
        return None

    return {
        "device_type": _known_device_type(
            context_device.get("device_type"),
            custom_data.get("_bk_device_type"),
            custom_data.get("device_type"),
            parsed["device_type"],
        ),
        "device_os": _known_text(
            context_device.get("device_os"),
            custom_data.get("_bk_device_os"),
            custom_data.get("device_os"),
            custom_data.get("os_name"),
            parsed["device_os"],
        ),
        "device_browser": _known_text(
            context_device.get("device_browser"),
            custom_data.get("_bk_device_browser"),
            custom_data.get("device_browser"),
            custom_data.get("browser_name"),
            parsed["device_browser"],
        ),
        "screen_width": _int_or_none(
            context_device.get("screen_width")
            or custom_data.get("_bk_screen_width")
            or custom_data.get("screen_width")
        ),
        "screen_height": _int_or_none(
            context_device.get("screen_height")
            or custom_data.get("_bk_screen_height")
            or custom_data.get("screen_height")
        ),
    }


def extract_event_custom_data(event_data: Any) -> dict:
    if hasattr(event_data, "model_dump"):
        event_data = event_data.model_dump()
    elif hasattr(event_data, "dict"):
        event_data = event_data.dict()
    if not isinstance(event_data, dict):
        return {}
    custom_data = event_data.get("custom_data") or {}
    return custom_data if isinstance(custom_data, dict) else {}


def geo_context_from_ip(ip_address: str | None) -> dict:
    loc = get_location_data(ip_address or "")
    city = _text(loc.get("ct"))
    region = _text(loc.get("st"))
    country = _text(loc.get("country"), 8)
    district = normalize_bd_district(city, region) if country == "bd" else None
    return {
        "geo_country": country,
        "geo_region": region,
        "geo_city": city,
        "geo_district": district,
    }
