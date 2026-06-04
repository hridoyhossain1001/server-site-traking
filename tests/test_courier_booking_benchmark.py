import pytest

from scripts.ops.benchmark_courier_booking_queue import fake_provider_response, run_benchmark


@pytest.mark.asyncio
async def test_synthetic_courier_booking_claim_benchmark_reports_throughput():
    result = await run_benchmark(job_count=25, iterations=2)

    assert result["mode"] == "synthetic"
    assert result["jobs_per_batch"] == 25
    assert result["iterations"] == 2
    assert result["average_ms"] >= 0
    assert result["p95_ms"] >= 0
    assert result["average_jobs_per_second"] > 0


@pytest.mark.asyncio
async def test_fake_provider_response_returns_successful_tracking_payload():
    result = await fake_provider_response(None, "steadfast", {}, "ORDER-123")

    assert result == {
        "success": True,
        "courier_order_id": "bench-provider-ORDER-123",
        "tracking_id": "bench-track-ORDER-123",
    }
