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
