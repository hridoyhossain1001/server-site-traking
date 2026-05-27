import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8')
from app.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.client import Client
import httpx

async def send_test_event():
    # Setup DB using app's central config
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Client).limit(1))
        client = result.scalar_one_or_none()

        if not client:
            print("No clients found in database.")
            return

        print(f"Testing with client: {client.name} (API Key: {client.api_key})")
        api_key = client.api_key

    url = "http://localhost:8000/api/v1/debug/test-event"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "event_name": "Purchase",
        "value": 1500.0,
        "currency": "BDT",
        "custom_params": {
            "test_param": "test_value_123"
        }
    }

    print("Sending POST request to:", url)
    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.post(url, headers=headers, json=payload, timeout=30.0)
            print("Status Code:", response.status_code)
            print("Response:", response.text)
        except Exception as e:
            print("Error making request:", repr(e))

if __name__ == "__main__":
    asyncio.run(send_test_event())
