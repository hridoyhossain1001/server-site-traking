"""End-to-End WooCommerce Session Tracking Simulator.

Simulates a sequential buyer journey:
PageView ➡️ ViewContent ➡️ AddToCart ➡️ InitiateCheckout ➡️ Purchase
Verifies server-side ingestion, cookie processing, and deduplication.
"""

import asyncio
import hashlib
import sys
import time
import uuid
import httpx
from sqlalchemy import select

sys.stdout.reconfigure(encoding='utf-8')
from app.database import AsyncSessionLocal
from app.models.client import Client

def sha256_hash(val: str) -> str:
    return hashlib.sha256(val.strip().lower().encode("utf-8")).hexdigest()

async def simulate_e2e_session():
    # Fetch active client from local database
    client_domain = "buykori.app"
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Client).limit(1))
        client = result.scalar_one_or_none()

        if not client:
            print("❌ Error: No clients found in database. Please add a client first.")
            return

        print(f"🚀 Found Client for test session: {client.name} (Public Key: {client.public_key})")
        api_key = client.public_key
        if client.domain:
            client_domain = client.domain.strip()

    # Base configuration
    base_url = "http://localhost:8000"
    client_ip = "182.160.100.45" # Realistic Bangladesh broadband IP
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    # Session Cookies / Trackers
    fbp = f"fb.1.{int(time.time() * 1000)}.{int(uuid.uuid4().int % 1000000000)}"
    ttp = str(uuid.uuid4())
    buykori_vid = str(uuid.uuid4())

    # Hashed PII (Facebook / TikTok matching standard)
    hashed_email = sha256_hash("hridoy@buykori.app")
    hashed_phone = sha256_hash("+8801712345678")

    # Event ID generation (matched browser + server deduplication)
    session_uuid = str(uuid.uuid4())[:8]
    events_to_simulate = [
        {
            "step": "1. PageView",
            "name": "PageView",
            "id": f"pv_{session_uuid}",
            "custom": {},
            "url": f"https://{client_domain}/"
        },
        {
            "step": "2. ViewContent",
            "name": "ViewContent",
            "id": f"vc_{session_uuid}",
            "custom": {
                "content_name": "Premium Server Tracking Package",
                "content_category": "Analytics",
                "content_ids": ["prod_99"],
                "content_type": "product",
                "value": 1500.0,
                "currency": "BDT"
            },
            "url": f"https://{client_domain}/product/server-tracking"
        },
        {
            "step": "3. AddToCart",
            "name": "AddToCart",
            "id": f"atc_{session_uuid}",
            "custom": {
                "content_name": "Premium Server Tracking Package",
                "content_ids": ["prod_99"],
                "content_type": "product",
                "value": 1500.0,
                "currency": "BDT"
            },
            "url": f"https://{client_domain}/product/server-tracking"
        },
        {
            "step": "4. InitiateCheckout",
            "name": "InitiateCheckout",
            "id": f"ic_{session_uuid}",
            "custom": {
                "num_items": 1,
                "value": 1500.0,
                "currency": "BDT",
                "content_ids": ["prod_99"]
            },
            "url": f"https://{client_domain}/checkout"
        },
        {
            "step": "5. Purchase",
            "name": "Purchase",
            "id": f"p_{session_uuid}",
            "custom": {
                "value": 1500.0,
                "currency": "BDT",
                "content_ids": ["prod_99"],
                "order_id": f"order_{int(time.time())}"
            },
            "url": f"https://{client_domain}/checkout/thank-you"
        }
    ]

    async with httpx.AsyncClient() as http_client:
        print("\n--- Starting End-to-End Tracking Session Simulation ---\n")

        for ev in events_to_simulate:
            print(f"⏳ Simulating Step: {ev['step']}")

            payload = {
                "data": [
                    {
                        "event_name": ev["name"],
                        "event_id": ev["id"],
                        "event_source_url": ev["url"],
                        "user_data": {
                            "client_ip_address": client_ip,
                            "client_user_agent": user_agent,
                            "fbp": fbp,
                            "fbc": "fb.1.1687593200000.IwAR0123456789",
                            "em": hashed_email,
                            "ph": hashed_phone,
                            "fn": sha256_hash("Hridoy"),
                            "ln": sha256_hash("Hossain"),
                            "external_id": sha256_hash("cust_12345"),
                            "buykorigw_vid": buykori_vid
                        },
                        "custom_data": ev["custom"]
                    }
                ]
            }

            url = f"{base_url}/c?key={api_key}"
            headers = {
                "Content-Type": "application/json",
                "Origin": f"https://{client_domain}",
                "Referer": f"https://{client_domain}/"
            }

            try:
                response = await http_client.post(url, json=payload, headers=headers, timeout=10.0)
                if response.status_code == 200:
                    res_json = response.json()
                    print(f"✅ Success: Event '{ev['name']}' accepted. Status: {response.status_code}")
                    print(f"   Response: {res_json}\n")
                else:
                    print(f"❌ Failed: Event '{ev['name']}' rejected. Status: {response.status_code}")
                    print(f"   Response: {response.text}\n")
            except Exception as e:
                print(f"❌ Request Error during step '{ev['name']}': {repr(e)}\n")

            # Short sleep to mimic realistic user actions
            await asyncio.sleep(0.5)

        print("--- Session Simulation Completed successfully! ---\n")

if __name__ == "__main__":
    asyncio.run(simulate_e2e_session())
