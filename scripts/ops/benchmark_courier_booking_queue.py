"""Measure courier booking queue overhead without provider network calls."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import statistics
import time
import uuid
from pathlib import Path
from types import SimpleNamespace

WORKSPACE = Path(__file__).resolve().parents[2]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from sqlalchemy import delete, func, select

from app.database import AsyncSessionLocal, Base, engine
from app.models.client import Client
from app.models.courier_booking_job import CourierBookingJob
from app.models.courier_order import CourierOrder
from app.models.pending_event import PendingEvent
from app.services import courier_booking_service


class _Rows:
    def __init__(self, jobs):
        self.jobs = jobs

    def scalars(self):
        return self

    def all(self):
        return self.jobs


class _SyntheticDb:
    def __init__(self, job_count: int):
        self.jobs = [
            SimpleNamespace(
                id=index,
                courier_order_id=index,
                status="queued",
                locked_at=None,
                locked_by=None,
            )
            for index in range(1, job_count + 1)
        ]
        self.orders = {
            index: SimpleNamespace(courier_status="booking_queued")
            for index in range(1, job_count + 1)
        }

    async def execute(self, _query):
        return _Rows(self.jobs)

    async def get(self, model, object_id):
        if model is CourierOrder:
            return self.orders.get(object_id)
        return None

    async def commit(self):
        return None

    async def rollback(self):
        return None


async def run_benchmark(job_count: int, iterations: int) -> dict:
    durations_ms = []
    for _ in range(iterations):
        db = _SyntheticDb(job_count)
        started = time.perf_counter()
        claimed = await courier_booking_service.claim_due_booking_jobs(db, limit=job_count)
        durations_ms.append((time.perf_counter() - started) * 1000)
        if len(claimed) != job_count:
            raise RuntimeError(f"Expected {job_count} claimed jobs, got {len(claimed)}")

    average_ms = statistics.mean(durations_ms)
    sorted_ms = sorted(durations_ms)
    p95_index = min(len(sorted_ms) - 1, int(len(sorted_ms) * 0.95))
    return {
        "mode": "synthetic",
        "jobs_per_batch": job_count,
        "iterations": iterations,
        "average_ms": round(average_ms, 3),
        "p95_ms": round(sorted_ms[p95_index], 3),
        "average_jobs_per_second": round(job_count / (average_ms / 1000), 1),
    }


async def fake_provider_response(_client: Client, _provider: str, _payload: dict, order_id: str) -> dict:
    return {
        "success": True,
        "courier_order_id": f"bench-provider-{order_id}",
        "tracking_id": f"bench-track-{order_id}",
    }


async def _create_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _seed_db_jobs(job_count: int, prefix: str) -> int:
    payload = {
        "recipient_name": "Benchmark Customer",
        "recipient_phone": "01837224409",
        "recipient_address": "Dhaka",
        "cod_amount": 150,
    }
    async with AsyncSessionLocal() as db:
        client = Client(
            name=f"Courier Queue Benchmark {prefix}",
            api_key=f"{prefix}-api",
            public_key=f"{prefix}-public",
            pixel_id="benchmark-pixel",
            access_token="benchmark-token",
            steadfast_api_key="benchmark-key",
            steadfast_secret_key="benchmark-secret",
            default_courier="steadfast",
        )
        db.add(client)
        await db.flush()

        pending_events = [
            PendingEvent(
                client_id=client.id,
                order_id=f"{prefix}-{index}",
                event_data={"event_name": "Purchase", "event_id": f"{prefix}-{index}"},
                raw_order_data=dict(payload),
                status="courier_booking_queued",
                portal_state="processing",
                is_confirmed=True,
            )
            for index in range(1, job_count + 1)
        ]
        db.add_all(pending_events)
        await db.flush()

        courier_orders = [
            CourierOrder(
                client_id=client.id,
                pending_event_id=pending.id,
                order_id=pending.order_id,
                courier_provider="steadfast",
                courier_status="booking_queued",
                recipient_name=payload["recipient_name"],
                recipient_phone=payload["recipient_phone"],
                recipient_address=payload["recipient_address"],
                cod_amount=payload["cod_amount"],
                status_history=[],
            )
            for pending in pending_events
        ]
        db.add_all(courier_orders)
        await db.flush()

        db.add_all(
            [
                CourierBookingJob(
                    client_id=client.id,
                    pending_event_id=pending.id,
                    courier_order_id=order.id,
                    provider="steadfast",
                    request_payload=dict(payload),
                    status="queued",
                )
                for pending, order in zip(pending_events, courier_orders)
            ]
        )
        await db.commit()
        return client.id


async def _cleanup_db_jobs(client_id: int | None) -> None:
    if not client_id:
        return
    async with AsyncSessionLocal() as db:
        await db.execute(delete(CourierBookingJob).where(CourierBookingJob.client_id == client_id))
        await db.execute(delete(CourierOrder).where(CourierOrder.client_id == client_id))
        await db.execute(delete(PendingEvent).where(PendingEvent.client_id == client_id))
        await db.execute(delete(Client).where(Client.id == client_id))
        await db.commit()


def _chunks(values: list[int], size: int):
    for index in range(0, len(values), size):
        yield values[index : index + size]


async def _count_sent_jobs(client_id: int) -> int:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.count())
            .select_from(CourierBookingJob)
            .where(CourierBookingJob.client_id == client_id, CourierBookingJob.status == "sent")
        )
        return int(result.scalar_one() or 0)


async def run_db_benchmark(
    job_count: int,
    batch_size: int,
    concurrency: int,
    *,
    create_schema: bool = False,
    keep_data: bool = False,
) -> dict:
    if create_schema:
        await _create_schema()

    prefix = f"bench-{uuid.uuid4().hex}"
    client_id: int | None = None
    original_provider = courier_booking_service._send_to_provider
    started_total = time.perf_counter()
    try:
        started_seed = time.perf_counter()
        client_id = await _seed_db_jobs(job_count, prefix)
        seed_ms = (time.perf_counter() - started_seed) * 1000

        claimed_ids: list[int] = []
        started_claim = time.perf_counter()
        while len(claimed_ids) < job_count:
            async with AsyncSessionLocal() as db:
                claimed = await courier_booking_service.claim_due_booking_jobs(db, limit=batch_size)
            if not claimed:
                break
            claimed_ids.extend(claimed)
        claim_ms = (time.perf_counter() - started_claim) * 1000
        if len(claimed_ids) != job_count:
            raise RuntimeError(f"Expected {job_count} claimed jobs, got {len(claimed_ids)}")

        courier_booking_service._send_to_provider = fake_provider_response
        started_process = time.perf_counter()
        for chunk in _chunks(claimed_ids, concurrency):
            await asyncio.gather(*(courier_booking_service.process_booking_job(job_id) for job_id in chunk))
        process_ms = (time.perf_counter() - started_process) * 1000

        sent_jobs = await _count_sent_jobs(client_id)
        total_ms = (time.perf_counter() - started_total) * 1000
        return {
            "mode": "db",
            "jobs": job_count,
            "batch_size": batch_size,
            "concurrency": concurrency,
            "seed_ms": round(seed_ms, 3),
            "claim_ms": round(claim_ms, 3),
            "process_ms": round(process_ms, 3),
            "total_ms": round(total_ms, 3),
            "jobs_per_second": round(job_count / (total_ms / 1000), 1),
            "claimed_jobs": len(claimed_ids),
            "sent_jobs": sent_jobs,
            "provider": "fake",
            "cleanup": "kept" if keep_data else "deleted",
        }
    finally:
        courier_booking_service._send_to_provider = original_provider
        if not keep_data:
            await _cleanup_db_jobs(client_id)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("synthetic", "db"), default="synthetic")
    parser.add_argument("--jobs", type=int, default=1000)
    parser.add_argument("--iterations", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--create-schema", action="store_true")
    parser.add_argument("--keep-data", action="store_true")
    args = parser.parse_args()
    if args.jobs < 1 or args.iterations < 1 or args.batch_size < 1 or args.concurrency < 1:
        parser.error("--jobs, --iterations, --batch-size, and --concurrency must be positive")

    if args.mode == "synthetic":
        result = asyncio.run(run_benchmark(args.jobs, args.iterations))
    else:
        result = asyncio.run(
            run_db_benchmark(
                args.jobs,
                args.batch_size,
                args.concurrency,
                create_schema=args.create_schema,
                keep_data=args.keep_data,
            )
        )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
