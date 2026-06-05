from app.routers.events import _best_request_device
from app.services.visitor_context import extract_device_metadata, normalize_bd_district


def test_normalize_bd_district_aliases():
    assert normalize_bd_district("Dacca") == "Dhaka"
    assert normalize_bd_district("Chittagong") == "Chattogram"
    assert normalize_bd_district("Coxs Bazar") == "Cox's Bazar"
    assert normalize_bd_district("Jessore") == "Jashore"


def test_extract_device_metadata_prefers_tracker_payload():
    metadata = extract_device_metadata(
        {
            "_bk_device_type": "mobile",
            "_bk_device_os": "Android",
            "_bk_device_browser": "Chrome",
            "_bk_screen_width": "393",
            "_bk_screen_height": "873",
        },
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125.0",
    )

    assert metadata["device_type"] == "mobile"
    assert metadata["device_os"] == "Android"
    assert metadata["device_browser"] == "Chrome"
    assert metadata["screen_width"] == 393
    assert metadata["screen_height"] == 873


def test_extract_device_metadata_accepts_tracker_endpoint_names():
    metadata = extract_device_metadata(
        {"device_type": "PC", "os_name": "Windows", "browser_name": "Chrome"},
        user_agent=None,
    )

    assert metadata["device_type"] == "desktop"
    assert metadata["device_os"] == "Windows"
    assert metadata["device_browser"] == "Chrome"


def test_extract_device_metadata_falls_back_when_tracker_values_are_unknown():
    metadata = extract_device_metadata(
        {
            "_bk_device_type": "unknown",
            "_bk_device_os": "Unknown",
            "_bk_device_browser": "Unknown",
        },
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
        ),
    )

    assert metadata["device_type"] == "desktop"
    assert metadata["device_os"] == "Windows"
    assert metadata["device_browser"] == "Chrome"


class _CustomData:
    def __init__(self, data):
        self._data = data

    def model_dump(self):
        return dict(self._data)


class _Event:
    def __init__(self, custom_data):
        self.custom_data = _CustomData(custom_data) if custom_data is not None else None


def test_best_request_device_prefers_enriched_tracker_payload_over_unknown_user_agent():
    device = _best_request_device(
        [
            _Event({}),
            _Event(
                {
                    "_bk_device_type": "desktop",
                    "_bk_device_os": "Windows",
                    "_bk_device_browser": "Chrome",
                    "_bk_screen_width": 1680,
                    "_bk_screen_height": 1050,
                }
            ),
        ],
        user_agent="WordPress/6.7; https://example.com",
    )

    assert device["device_type"] == "desktop"
    assert device["device_os"] == "Windows"
    assert device["device_browser"] == "Chrome"
    assert device["screen_width"] == 1680
