"""
Plugin Update Check Router
───────────────────────────
WordPress প্লাগইনের অটো-আপডেট সিস্টেমের জন্য সার্ভার-সাইড endpoint।
প্লাগইন এই endpoint-এ রিকোয়েস্ট পাঠিয়ে নতুন ভার্সন আছে কিনা চেক করে।
"""

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(tags=["Plugin"])

# Current plugin version — নতুন ভার্সন রিলিজ করলে এখানে আপডেট করুন
PLUGIN_VERSION = os.getenv("PLUGIN_VERSION", "1.1.0")
PLUGIN_ZIP_PATH = Path(
    os.getenv(
        "PLUGIN_ZIP_PATH",
        str(Path(__file__).resolve().parents[2] / "wordpress-plugin" / "capi-gateway.zip"),
    )
)
PLUGIN_DOWNLOAD_URL = os.getenv(
    "PLUGIN_DOWNLOAD_URL",
    "https://still-stream-48626-bb0ac4cda957.herokuapp.com/api/v1/plugin/download"
)


@router.get(
    "/plugin/update-check",
    summary="Check for plugin updates",
    description="WordPress প্লাগইন এই endpoint-এ রিকোয়েস্ট পাঠিয়ে নতুন ভার্সন চেক করে।",
)
async def plugin_update_check():
    """Return current plugin version info for WordPress auto-updater."""
    return JSONResponse(content={
        "version": PLUGIN_VERSION,
        "download_url": PLUGIN_DOWNLOAD_URL,
        "homepage": "https://still-stream-48626-bb0ac4cda957.herokuapp.com/",
        "requires": "5.8",
        "tested": "6.7",
        "requires_php": "7.4",
        "last_updated": "2026-05-16",
        "description": "Server-Side Facebook CAPI, TikTok, and GA4 tracking for WooCommerce with deferred purchase support.",
        "changelog": "<h4>v1.1.0</h4><ul>"
                     "<li>🔒 Purchase event blocking request — response verification</li>"
                     "<li>🔒 Phone hash normalization fix — Python/PHP matching</li>"
                     "<li>🔒 WooCommerce webhook HMAC signature verification</li>"
                     "<li>⚡ Atomic rate limiting — race condition free</li>"
                     "<li>⚡ Production database safety</li>"
                     "</ul>"
                     "<h4>v1.0.0</h4><ul>"
                     "<li>Initial release</li>"
                     "<li>PageView, ViewContent, AddToCart, InitiateCheckout, Purchase tracking</li>"
                     "<li>Deferred Purchase with auto-confirm</li>"
                     "<li>Action Scheduler retry queue</li>"
        "</ul>",
    })


@router.get(
    "/plugin/download",
    summary="Download WordPress plugin ZIP",
    include_in_schema=False,
)
async def plugin_download():
    """Serve the packaged WordPress plugin ZIP for the auto-updater."""
    if not PLUGIN_ZIP_PATH.is_file():
        raise HTTPException(status_code=404, detail="Plugin ZIP not found")

    return FileResponse(
        path=PLUGIN_ZIP_PATH,
        media_type="application/zip",
        filename="capi-gateway.zip",
    )
