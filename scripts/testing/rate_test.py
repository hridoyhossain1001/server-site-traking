import asyncio
import httpx
import time
import os

API_KEY = os.getenv("TEST_API_KEY", "")
URL = os.getenv("TEST_URL", "http://localhost:8000/api/v1/events")

async def send_request(client, i):
    payload = {
        "data": [{
            "event_name": f"RateTest_{i}",
            "event_time": int(time.time()),
            "event_id": f"rate_{time.time_ns()}_{i}",
            "user_data": {"client_ip_address": "127.0.0.1"}
        }]
    }
    headers = {"X-API-Key": API_KEY}
    return await client.post(URL, json=payload, headers=headers)

async def main():
    if not API_KEY:
        raise SystemExit("Set TEST_API_KEY before running the rate test.")

    print("Firing 50 rapid requests to test rate limit (set to 5 per worker)...")
    async with httpx.AsyncClient() as client:
        tasks = [send_request(client, i) for i in range(50)]
        responses = await asyncio.gather(*tasks)

    status_codes = [r.status_code for r in responses]
    print(f"Status codes: {status_codes}")

    success = status_codes.count(200)
    limited = status_codes.count(429)
    print(f"Success (200): {success}")
    print(f"Rate Limited (429): {limited}")

if __name__ == "__main__":
    asyncio.run(main())
