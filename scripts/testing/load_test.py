import asyncio
import os
import time
import httpx

API_KEY = os.getenv("CAPI_LOAD_TEST_API_KEY")
URL = os.getenv("CAPI_LOAD_TEST_URL", "http://localhost:8000/api/v1/events")
CONCURRENCY = int(os.getenv("CAPI_LOAD_TEST_CONCURRENCY", "80"))
TOTAL_REQUESTS = int(os.getenv("CAPI_LOAD_TEST_REQUESTS", "1000"))

async def send_request(client, i):
    data = {
        "data": [
            {
                "event_name": "PageView",
                "event_time": int(time.time()),
                "event_id": f"pv_load_{int(time.time())}_{i}",
                "event_source_url": "http://example.com/test",
                "user_data": {
                    "client_ip_address": "1.2.3.4",
                    "client_user_agent": "LoadTester"
                }
            },
            {
                "event_name": "ViewContent",
                "event_time": int(time.time()),
                "event_id": f"vc_load_{int(time.time())}_{i}",
                "event_source_url": "http://example.com/test",
                "user_data": {
                    "client_ip_address": "1.2.3.4",
                    "client_user_agent": "LoadTester"
                }
            },
            {
                "event_name": "AddToCart",
                "event_time": int(time.time()),
                "event_id": f"atc_load_{int(time.time())}_{i}",
                "event_source_url": "http://example.com/test",
                "user_data": {
                    "client_ip_address": "1.2.3.4",
                    "client_user_agent": "LoadTester"
                }
            }
        ],
        "test_event_code": "TEST12345"
    }

    headers = {
        "X-API-Key": API_KEY,
        "Origin": "https://test-website-fget.vercel.app"
    }

    start_time = time.time()
    try:
        response = await client.post(URL, json=data, headers=headers)
        return response.status_code, time.time() - start_time
    except Exception as e:
        return e.__class__.__name__, time.time() - start_time

async def main():
    if not API_KEY:
        raise SystemExit("Set CAPI_LOAD_TEST_API_KEY before running the load test.")

    concurrency = CONCURRENCY
    total_requests = TOTAL_REQUESTS

    print(f"Starting load test: {total_requests} requests with {concurrency} concurrency...")

    async with httpx.AsyncClient(timeout=30.0, limits=httpx.Limits(max_connections=concurrency)) as client:
        tasks = []
        start_overall = time.time()
        for i in range(total_requests):
            tasks.append(send_request(client, i))

        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_overall

    status_counts = {}
    for status, duration in results:
        status_counts[status] = status_counts.get(status, 0) + 1

    print(f"\nResults in {total_time:.2f} seconds:")
    for status, count in status_counts.items():
        print(f"Status {status}: {count}")

    print(f"Requests per second: {total_requests / total_time:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
