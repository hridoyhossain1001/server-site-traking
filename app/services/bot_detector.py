"""
Bot Detection Service — বট ট্রাফিক ফিল্টার করে ডেটা কোয়ালিটি বাড়ায়।
পরিচিত বট User-Agent ও সন্দেহজনক প্যাটার্ন চেক করে।
"""

import re
import logging

logger = logging.getLogger(__name__)

# ─── পরিচিত বটের User-Agent প্যাটার্ন ──────────────────────────────────────
# এই লিস্টে থাকা কোনো কিওয়ার্ড User-Agent-এ পাওয়া গেলে বট হিসেবে গণ্য হবে
BOT_PATTERNS = [
    # Search Engine Crawlers
    "googlebot", "bingbot", "slurp", "duckduckbot", "baiduspider",
    "yandexbot", "sogou", "exabot", "ia_archiver",
    # Social Media Crawlers
    "facebookexternalhit", "facebot", "twitterbot", "linkedinbot",
    "pinterestbot", "telegrambot", "whatsapp", "slackbot", "discordbot",
    # SEO & Monitoring Tools
    "semrushbot", "ahrefsbot", "mj12bot", "dotbot", "rogerbot",
    "screaming frog", "seokicks", "sistrix",
    # Generic Bot Indicators
    "bot/", "crawler", "spider", "scraper", "headless",
    "phantomjs", "selenium", "puppeteer", "playwright",
    "wget", "curl/", "python-requests", "python-urllib",
    "go-http-client", "java/", "apache-httpclient",
    "node-fetch", "axios/", "libwww-perl",
    # Uptime / Monitoring
    "uptimerobot", "pingdom", "statuscake", "site24x7",
    "newrelicpinger", "datadog",
]

# ─── Compiled regex for fast matching ────────────────────────────────────────
_BOT_REGEX = re.compile("|".join(re.escape(p) for p in BOT_PATTERNS), re.IGNORECASE)


def is_bot(user_agent: str | None) -> bool:
    """
    User-Agent স্ট্রিং চেক করে বট কিনা নির্ণয় করে।

    Returns:
        True = বট (ইভেন্ট ড্রপ করতে হবে)
        False = রিয়েল ইউজার (ইভেন্ট পাঠাতে হবে)
    """
    if not user_agent or len(user_agent.strip()) < 10:
        # খালি বা অতি ছোট User-Agent সাধারণত বট
        logger.info(f"🤖 Bot detected: Empty/short User-Agent")
        return True

    if _BOT_REGEX.search(user_agent):
        logger.info(f"🤖 Bot detected: {user_agent[:80]}...")
        return True

    return False
