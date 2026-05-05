import asyncio
import time
import httpx

API_KEY = "8ywUZzNpEaZA2_lOVTgHKU5H5DGz-1UVAbEuKvnY9uo"
URL = "https://still-stream-48626-bb0ac4cda957.herokuapp.com/api/v1/events"

async def send_request(client, i):
    data = {
        "data": [
            {
                "event_name": "PageView",
                "event_time": int(time.time()),
                "event_id": f"test_load_{int(time.time())}_{i}",
                "event_source_url": "http://example.com/test",
                "user_data": {
                    "client_ip_address": "1.2.3.4",
                    "client_user_agent": "LoadTester"
                }
            }
        ],
        "test_event_code": "TEST12345"
    }
    
    headers = {"X-API-Key": API_KEY}
    
    start_time = time.time()
    try:
        response = await client.post(URL, json=data, headers=headers)
        return response.status_code, time.time() - start_time
    except Exception as e:
        return e.__class__.__name__, time.time() - start_time

async def main():
    concurrency = 80
    total_requests = 1000
    
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
