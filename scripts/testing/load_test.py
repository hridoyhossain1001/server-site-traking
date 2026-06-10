import argparse
import asyncio
import hashlib
import hmac
import json
import os
import random
import statistics
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import httpx


DEFAULT_EVENTS_URL = "http://localhost:8000/api/v1/events"
DEFAULT_TRACKER_URL = "http://localhost:8000/c"
PRODUCTION_HOSTS = {"api.buykori.app", "www.api.buykori.app"}

SAFE_EVENT_MIX = {
    "PageView": 45,
    "ViewContent": 30,
    "AddToCart": 15,
    "InitiateCheckout": 10,
}
FULL_EVENT_MIX = {
    **SAFE_EVENT_MIX,
    "Purchase": 3,
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
]


@dataclass
class Stats:
    started_at: float = field(default_factory=time.perf_counter)
    latencies: list[float] = field(default_factory=list)
    statuses: Counter[str] = field(default_factory=Counter)
    errors: Counter[str] = field(default_factory=Counter)
    response_messages: Counter[str] = field(default_factory=Counter)
    event_counts: Counter[str] = field(default_factory=Counter)
    sent_requests: int = 0
    sent_events: int = 0
    accepted_events: int = 0

    def record_latency(self, value: float) -> None:
        self.latencies.append(value)

    def snapshot(self) -> dict[str, Any]:
        elapsed = max(time.perf_counter() - self.started_at, 0.001)
        sorted_latencies = sorted(self.latencies)

        def percentile(p: float) -> float:
            if not sorted_latencies:
                return 0.0
            index = min(len(sorted_latencies) - 1, int(len(sorted_latencies) * p / 100))
            return sorted_latencies[index] * 1000

        latency_summary = {}
        if sorted_latencies:
            latency_summary = {
                "avg_ms": round(statistics.fmean(sorted_latencies) * 1000, 2),
                "p50_ms": round(percentile(50), 2),
                "p95_ms": round(percentile(95), 2),
                "p99_ms": round(percentile(99), 2),
                "max_ms": round(max(sorted_latencies) * 1000, 2),
            }

        return {
            "elapsed_seconds": round(elapsed, 2),
            "sent_requests": self.sent_requests,
            "sent_events": self.sent_events,
            "accepted_events": self.accepted_events,
            "actual_request_rps": round(self.sent_requests / elapsed, 2),
            "actual_event_rps": round(self.sent_events / elapsed, 2),
            "statuses": dict(self.statuses),
            "errors": dict(self.errors),
            "response_messages": dict(self.response_messages),
            "event_mix": dict(self.event_counts),
            "latency": latency_summary,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Production-safe Buykori mixed event load test harness."
    )
    parser.add_argument(
        "--mode",
        choices=["events", "tracker"],
        default=os.getenv("CAPI_LOAD_TEST_MODE", "events"),
        help="/api/v1/events signed server route or /c browser tracker route.",
    )
    parser.add_argument("--url", default=os.getenv("CAPI_LOAD_TEST_URL"))
    parser.add_argument("--api-key", default=os.getenv("CAPI_LOAD_TEST_API_KEY", ""))
    parser.add_argument("--public-key", default=os.getenv("CAPI_LOAD_TEST_PUBLIC_KEY", ""))
    parser.add_argument(
        "--origin",
        default=os.getenv("CAPI_LOAD_TEST_ORIGIN", "https://loadtest.buykori.local"),
        help="Locked site origin used for Origin/Referer and signed X-CAPI-Origin.",
    )
    parser.add_argument("--rps", type=float, default=float(os.getenv("CAPI_LOAD_TEST_RPS", "10")))
    parser.add_argument(
        "--duration",
        type=int,
        default=int(os.getenv("CAPI_LOAD_TEST_DURATION", "60")),
        help="Run length in seconds.",
    )
    parser.add_argument(
        "--max-requests",
        type=int,
        default=int(os.getenv("CAPI_LOAD_TEST_MAX_REQUESTS", "0")),
        help="Optional request cap. 0 means duration*rps.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=int(os.getenv("CAPI_LOAD_TEST_CONCURRENCY", "20")),
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=int(os.getenv("CAPI_LOAD_TEST_BATCH_SIZE", "1")),
        help="Events per request. Keep this low for realistic browser/server behavior.",
    )
    parser.add_argument(
        "--include-purchase",
        action="store_true",
        default=os.getenv("CAPI_LOAD_TEST_INCLUDE_PURCHASE", "").lower() in {"1", "true", "yes"},
        help="Include Purchase in the mix. Off by default to avoid creating test orders/holds.",
    )
    parser.add_argument(
        "--http2",
        action="store_true",
        default=os.getenv("CAPI_LOAD_TEST_HTTP2", "").lower() in {"1", "true", "yes"},
    )
    parser.add_argument("--timeout", type=float, default=float(os.getenv("CAPI_LOAD_TEST_TIMEOUT", "15")))
    parser.add_argument("--run-id", default=os.getenv("CAPI_LOAD_TEST_RUN_ID") or f"lt_{int(time.time())}")
    parser.add_argument("--seed", type=int, default=int(os.getenv("CAPI_LOAD_TEST_SEED", "20260606")))
    parser.add_argument("--dry-run", action="store_true", help="Print one signed sample and exit.")
    parser.add_argument(
        "--unsafe-production-ok",
        action="store_true",
        default=os.getenv("CAPI_LOAD_TEST_UNSAFE_PRODUCTION_OK", "").lower() in {"1", "true", "yes"},
        help="Required for api.buykori.app to prevent accidental platform-spam tests.",
    )
    parser.add_argument("--json-output", default=os.getenv("CAPI_LOAD_TEST_JSON_OUTPUT", ""))
    return parser.parse_args()


def compact_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def signed_headers(api_key: str, origin: str, body: str) -> dict[str, str]:
    timestamp = str(int(time.time()))
    signature = hmac.new(
        api_key.encode("utf-8"),
        f"{timestamp}.{body}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return {
        "X-API-Key": api_key,
        "X-CAPI-Origin": origin,
        "X-CAPI-Timestamp": timestamp,
        "X-CAPI-Signature": signature,
        "Origin": origin,
        "Referer": f"{origin.rstrip('/')}/load-test",
        "Content-Type": "application/json",
    }


def event_mix(include_purchase: bool) -> list[str]:
    weighted = FULL_EVENT_MIX if include_purchase else SAFE_EVENT_MIX
    events: list[str] = []
    for name, weight in weighted.items():
        events.extend([name] * weight)
    return events


def device_for_index(index: int) -> dict[str, Any]:
    user_agent = USER_AGENTS[index % len(USER_AGENTS)]
    if "iPhone" in user_agent:
        return {
            "user_agent": user_agent,
            "type": "Mobile",
            "os": "iOS",
            "browser": "Safari",
            "screen_width": 390,
            "screen_height": 844,
        }
    if "Android" in user_agent:
        return {
            "user_agent": user_agent,
            "type": "Mobile",
            "os": "Android",
            "browser": "Chrome",
            "screen_width": 412,
            "screen_height": 915,
        }
    if "Macintosh" in user_agent:
        return {
            "user_agent": user_agent,
            "type": "Desktop",
            "os": "macOS",
            "browser": "Safari",
            "screen_width": 1440,
            "screen_height": 900,
        }
    return {
        "user_agent": user_agent,
        "type": "Desktop",
        "os": "Windows",
        "browser": "Chrome",
        "screen_width": 1536,
        "screen_height": 864,
    }


def user_data(index: int, run_id: str) -> dict[str, Any]:
    now_ms = int(time.time() * 1000)
    visitor = f"{run_id}_visitor_{index % 5000}"
    return {
        "client_ip_address": f"203.0.113.{(index % 200) + 1}",
        "client_user_agent": device_for_index(index)["user_agent"],
        "fbp": f"fb.1.{now_ms}.{1000000000 + index}",
        "ttp": f"{run_id}_{index % 5000}_ttp",
        "external_id": [visitor],
    }


def custom_data(event_name: str, index: int) -> dict[str, Any]:
    product_id = str(240 + (index % 20))
    value = round(90 + ((index % 8) * 15), 2)
    device = device_for_index(index)
    base = {
        "_bk_device_type": device["type"],
        "_bk_device_os": device["os"],
        "_bk_device_browser": device["browser"],
        "_bk_screen_width": device["screen_width"],
        "_bk_screen_height": device["screen_height"],
    }
    if event_name == "PageView":
        return {
            **base,
            "content_name": "Load test landing",
            "content_category": "performance",
        }
    if event_name == "ViewContent":
        return {
            **base,
            "content_ids": [product_id],
            "content_type": "product",
            "content_name": f"Load product {product_id}",
            "contents": [{"id": product_id, "quantity": 1, "item_price": value}],
            "value": value,
            "currency": "BDT",
        }
    if event_name == "AddToCart":
        return {
            **base,
            "content_ids": [product_id],
            "content_type": "product",
            "contents": [{"id": product_id, "quantity": 1, "item_price": value}],
            "value": value,
            "currency": "BDT",
            "num_items": 1,
        }
    if event_name == "InitiateCheckout":
        return {
            **base,
            "content_ids": [product_id],
            "content_type": "product",
            "contents": [{"id": product_id, "quantity": 1, "item_price": value}],
            "value": value,
            "currency": "BDT",
            "num_items": 1,
        }
    return {
        **base,
        "content_ids": [product_id],
        "content_type": "product",
        "contents": [{"id": product_id, "quantity": 1, "item_price": value}],
        "value": value,
        "currency": "BDT",
        "order_id": f"load_order_{index}",
        "num_items": 1,
    }


def event_url(origin: str, event_name: str, index: int, run_id: str) -> str:
    path_by_event = {
        "PageView": "/",
        "ViewContent": f"/product/load-product-{240 + (index % 20)}",
        "AddToCart": f"/cart?add-to-cart={240 + (index % 20)}",
        "InitiateCheckout": "/checkout",
        "Purchase": f"/checkout/order-received/load-{index}",
    }
    path = path_by_event[event_name]
    separator = "&" if "?" in path else "?"
    return f"{origin.rstrip('/')}{path}{separator}utm_source=loadtest&utm_campaign={run_id}"


def make_event(index: int, run_id: str, origin: str, choices: list[str]) -> dict[str, Any]:
    event_name = random.choice(choices)
    event_id = f"{run_id}_{event_name}_{index}_{random.randint(100000, 999999)}"
    return {
        "event_name": event_name,
        "event_time": int(time.time()),
        "event_id": event_id,
        "event_source_url": event_url(origin, event_name, index, run_id),
        "action_source": "website",
        "user_data": user_data(index, run_id),
        "custom_data": custom_data(event_name, index),
    }


def make_payload(start_index: int, batch_size: int, run_id: str, origin: str, choices: list[str]) -> dict[str, Any]:
    return {
        "data": [
            make_event(start_index + offset, run_id, origin, choices)
            for offset in range(batch_size)
        ]
    }


def with_public_key(url: str, public_key: str) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query))
    query["key"] = public_key
    return urlunparse(parsed._replace(query=urlencode(query)))


def guard_args(args: argparse.Namespace) -> None:
    if args.rps <= 0:
        raise SystemExit("--rps must be greater than 0.")
    if args.duration <= 0:
        raise SystemExit("--duration must be greater than 0.")
    if args.concurrency <= 0:
        raise SystemExit("--concurrency must be greater than 0.")
    if args.batch_size <= 0 or args.batch_size > 50:
        raise SystemExit("--batch-size must be between 1 and 50.")

    if args.mode == "events":
        args.url = args.url or DEFAULT_EVENTS_URL
        if not args.api_key:
            raise SystemExit("Set --api-key or CAPI_LOAD_TEST_API_KEY for events mode.")
    else:
        args.url = args.url or DEFAULT_TRACKER_URL
        if not args.public_key:
            raise SystemExit("Set --public-key or CAPI_LOAD_TEST_PUBLIC_KEY for tracker mode.")
        args.url = with_public_key(args.url, args.public_key)

    host = (urlparse(args.url).hostname or "").lower()
    if host in PRODUCTION_HOSTS and not args.unsafe_production_ok:
        raise SystemExit(
            "Production URL detected. Re-run with --unsafe-production-ok only after "
            "using a dedicated LoadTest client with Meta/TikTok delivery disabled."
        )


async def send_once(
    client: httpx.AsyncClient,
    args: argparse.Namespace,
    index: int,
    choices: list[str],
    stats: Stats,
) -> None:
    payload = make_payload(index * args.batch_size, args.batch_size, args.run_id, args.origin, choices)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": device_for_index(index)["user_agent"],
    }
    body = compact_json(payload)
    if args.mode == "events":
        headers.update(signed_headers(args.api_key, args.origin, body))
    else:
        headers.update(
            {
                "Origin": args.origin,
                "Referer": f"{args.origin.rstrip('/')}/load-test",
            }
        )

    started = time.perf_counter()
    try:
        response = await client.post(args.url, content=body, headers=headers)
        elapsed = time.perf_counter() - started
        stats.record_latency(elapsed)
        stats.statuses[str(response.status_code)] += 1
        try:
            response_json = response.json()
            message = str(response_json.get("message") or response_json.get("status") or "unknown")
            stats.response_messages[message] += 1
            stats.accepted_events += int(response_json.get("events_received") or 0)
        except Exception:
            stats.response_messages[response.text[:80] or "empty"] += 1
    except Exception as exc:
        stats.record_latency(time.perf_counter() - started)
        stats.errors[type(exc).__name__] += 1
    finally:
        stats.sent_requests += 1
        stats.sent_events += len(payload["data"])
        for event in payload["data"]:
            stats.event_counts[event["event_name"]] += 1


async def worker(
    queue: asyncio.Queue[int | None],
    client: httpx.AsyncClient,
    args: argparse.Namespace,
    choices: list[str],
    stats: Stats,
) -> None:
    while True:
        item = await queue.get()
        try:
            if item is None:
                return
            await send_once(client, args, item, choices, stats)
        finally:
            queue.task_done()


async def run_load(args: argparse.Namespace) -> Stats:
    choices = event_mix(args.include_purchase)
    stats = Stats()
    queue: asyncio.Queue[int | None] = asyncio.Queue(maxsize=max(args.concurrency * 4, 1))
    limits = httpx.Limits(
        max_connections=args.concurrency,
        max_keepalive_connections=args.concurrency,
    )

    request_count = int(args.rps * args.duration)
    if args.max_requests > 0:
        request_count = min(request_count, args.max_requests)

    async with httpx.AsyncClient(
        timeout=args.timeout,
        http2=args.http2,
        limits=limits,
        follow_redirects=False,
    ) as client:
        tasks = [
            asyncio.create_task(worker(queue, client, args, choices, stats))
            for _ in range(args.concurrency)
        ]
        interval = 1.0 / args.rps
        start = time.perf_counter()
        next_send = start

        for index in range(request_count):
            now = time.perf_counter()
            if now < next_send:
                await asyncio.sleep(next_send - now)
            await queue.put(index)
            next_send += interval

        for _ in tasks:
            await queue.put(None)
        await queue.join()
        await asyncio.gather(*tasks)

    return stats


def print_dry_run(args: argparse.Namespace) -> None:
    choices = event_mix(args.include_purchase)
    payload = make_payload(0, args.batch_size, args.run_id, args.origin, choices)
    body = compact_json(payload)
    headers = signed_headers(args.api_key, args.origin, body) if args.mode == "events" else {
        "Origin": args.origin,
        "Referer": f"{args.origin.rstrip('/')}/load-test",
    }
    redacted_headers = dict(headers)
    if "X-API-Key" in redacted_headers:
        redacted_headers["X-API-Key"] = f"{headers['X-API-Key'][:6]}...redacted"
    print("Dry-run URL:")
    print(args.url)
    print("\nHeaders:")
    print(json.dumps(redacted_headers, indent=2))
    print("\nPayload:")
    print(json.dumps(payload, indent=2))


def write_json_output(path: str, summary: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(summary, indent=2), encoding="utf-8")


async def main() -> None:
    args = parse_args()
    guard_args(args)
    random.seed(args.seed)

    if args.dry_run:
        print_dry_run(args)
        return

    print(
        "Starting load test: "
        f"mode={args.mode} url={args.url} rps={args.rps:g} duration={args.duration}s "
        f"concurrency={args.concurrency} batch_size={args.batch_size} "
        f"include_purchase={args.include_purchase} http2={args.http2}"
    )
    stats = await run_load(args)
    summary = stats.snapshot()

    print("\nSummary:")
    print(json.dumps(summary, indent=2))
    if args.json_output:
        write_json_output(args.json_output, summary)
        print(f"\nWrote summary: {args.json_output}")


if __name__ == "__main__":
    asyncio.run(main())
