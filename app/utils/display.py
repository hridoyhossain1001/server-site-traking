"""
Shared display/formatting utilities — used by admin, client_portal, and templates.
Extracted from admin.py to avoid cross-router import coupling.
"""

from urllib.parse import urlparse


def normalize_domain_input(domain: str | None) -> str | None:
    """Domain input normalize করে — www, trailing dots, protocol সরায়।
    যদি comma-separated multiple domains থাকে, তবে প্রত্যেকটি ডোমেনকে normalize করে comma দিয়ে যুক্ত করে।
    """
    if not domain or not domain.strip():
        return None

    raw = domain.strip().lower()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        return None

    normalized_parts = []
    for part in parts:
        parsed = urlparse(part if "://" in part else f"https://{part}")
        host = (parsed.hostname or part).strip().rstrip(".")
        if host.startswith("www."):
            host = host[4:]
        if host:
            normalized_parts.append(host)

    return ",".join(normalized_parts) if normalized_parts else None


def display_domain_url(domain: str | None) -> str:
    """Domain থেকে display URL তৈরি করে (e.g., https://www.example.com)।
    যদি একাধিক comma-separated domains থাকে, তবে প্রথম ডোমেনটি নিয়ে কাজ করে।
    """
    if not domain:
        return ""
    parts = [p.strip() for p in domain.split(",") if p.strip()]
    if not parts:
        return ""
    first_domain = normalize_domain_input(parts[0])
    if not first_domain:
        return ""
    return f"https://www.{first_domain}"


def mask_secret(value: str | None, prefix: int = 6, suffix: int = 4) -> str:
    """Secret value-এর মাঝে bullet দিয়ে মাস্ক করে।"""
    if not value:
        return ""
    if len(value) <= prefix + suffix:
        return "•" * len(value)
    return f"{value[:prefix]}{'•' * 12}{value[-suffix:]}"
