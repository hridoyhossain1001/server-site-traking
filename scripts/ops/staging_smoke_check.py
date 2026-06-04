"""Read-only staging smoke checks for the Buykori backend rollout."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class SmokeResult:
    name: str
    ok: bool
    status_code: int | None = None
    message: str = ""
    payload: dict[str, Any] | None = None


def build_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/") + "/"
    return urljoin(base, path.lstrip("/"))


def fetch_json(url: str, *, headers: dict[str, str] | None = None, timeout: float = 10.0) -> tuple[int, dict[str, Any]]:
    request = Request(url, headers=headers or {})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body or "{}")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body or "{}")
        except json.JSONDecodeError:
            payload = {"error": body}
        return exc.code, payload
    except (OSError, URLError) as exc:
        raise RuntimeError(str(exc)) from exc


def evaluate_status(payload: dict[str, Any], *, allow_degraded: bool = False) -> tuple[bool, str]:
    status = str(payload.get("status") or "").lower()
    db_ok = payload.get("db")
    redis_ok = payload.get("redis")
    if status == "ok":
        return True, "status ok"
    if allow_degraded and status == "degraded" and db_ok is True:
        return True, f"status degraded but DB is healthy; redis={redis_ok}"
    return False, f"status={status or 'missing'} db={db_ok} redis={redis_ok}"


def evaluate_queue(payload: dict[str, Any], *, allow_queue_alerts: bool = False) -> tuple[bool, str]:
    queue = payload.get("courier_booking_queue") if "courier_booking_queue" in payload else payload
    if not isinstance(queue, dict):
        return False, "courier queue payload missing"
    alert_status = str(queue.get("alert_status") or "healthy").lower()
    queued = int(queue.get("queued") or 0)
    processing = int(queue.get("processing") or 0)
    dead = int(queue.get("dead") or 0)
    if alert_status == "critical" and not allow_queue_alerts:
        return False, f"queue critical: queued={queued} processing={processing} dead={dead}"
    return True, f"queue {alert_status}: queued={queued} processing={processing} dead={dead}"


def run_smoke(
    base_url: str,
    admin_api_key: str,
    *,
    timeout: float = 10.0,
    allow_degraded_status: bool = False,
    allow_queue_alerts: bool = False,
) -> list[SmokeResult]:
    admin_headers = {"X-Admin-API-Key": admin_api_key}
    checks: list[SmokeResult] = []

    try:
        status_code, payload = fetch_json(build_url(base_url, "/status"), timeout=timeout)
        ok = status_code == 200
        message = f"http {status_code}"
        if ok:
            ok, message = evaluate_status(payload, allow_degraded=allow_degraded_status)
        checks.append(SmokeResult("status", ok, status_code, message, payload))
    except RuntimeError as exc:
        checks.append(SmokeResult("status", False, None, str(exc)))

    try:
        status_code, payload = fetch_json(
            build_url(base_url, "/api/v1/admin/api/summary"),
            headers=admin_headers,
            timeout=timeout,
        )
        ok = status_code == 200
        message = f"http {status_code}"
        if ok:
            ok, message = evaluate_queue(payload, allow_queue_alerts=allow_queue_alerts)
        checks.append(SmokeResult("admin_summary", ok, status_code, message, payload))
    except RuntimeError as exc:
        checks.append(SmokeResult("admin_summary", False, None, str(exc)))

    try:
        status_code, payload = fetch_json(
            build_url(base_url, "/api/v1/admin/api/courier-booking-queue?limit=5"),
            headers=admin_headers,
            timeout=timeout,
        )
        ok = status_code == 200
        message = f"http {status_code}"
        if ok:
            ok, message = evaluate_queue(payload, allow_queue_alerts=allow_queue_alerts)
        checks.append(SmokeResult("courier_queue", ok, status_code, message, payload))
    except RuntimeError as exc:
        checks.append(SmokeResult("courier_queue", False, None, str(exc)))

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Run read-only staging smoke checks.")
    parser.add_argument("--base-url", default=os.getenv("STAGING_BASE_URL"))
    parser.add_argument("--admin-api-key", default=os.getenv("ADMIN_API_KEY"))
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--allow-degraded-status", action="store_true")
    parser.add_argument("--allow-queue-alerts", action="store_true")
    args = parser.parse_args()

    if not args.base_url:
        parser.error("--base-url or STAGING_BASE_URL is required")
    if not args.admin_api_key:
        parser.error("--admin-api-key or ADMIN_API_KEY is required")

    results = run_smoke(
        args.base_url,
        args.admin_api_key,
        timeout=args.timeout,
        allow_degraded_status=args.allow_degraded_status,
        allow_queue_alerts=args.allow_queue_alerts,
    )
    output = {
        "base_url": args.base_url.rstrip("/"),
        "ok": all(result.ok for result in results),
        "checks": [
            {
                "name": result.name,
                "ok": result.ok,
                "status_code": result.status_code,
                "message": result.message,
            }
            for result in results
        ],
    }
    print(json.dumps(output, indent=2))
    return 0 if output["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
