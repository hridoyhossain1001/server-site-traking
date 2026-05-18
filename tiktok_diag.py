import asyncio
import time
import json
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.client import Client
from app.services.tiktok_service import send_to_tiktok, _build_tiktok_payload
from app.schemas.event import EventData
from app.security import decrypt_token


async def run():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Client).where(Client.name.ilike('%shakil%')))
        client = res.scalar()
        if not client:
            print('ERROR: Client not found')
            return

        print(f'Client: {client.name}')
        print(f'TikTok Pixel ID: {client.tiktok_pixel_id}')
        print(f'TikTok Token exists: {bool(client.tiktok_access_token)}')
        print(f'Test Event Code: {client.test_event_code}')

        if not client.tiktok_pixel_id:
            print('ERROR: No TikTok Pixel ID configured!')
            return

        try:
            token = decrypt_token(client.tiktok_access_token)
            print(f'Token decrypted OK, starts with: {token[:20]}...')
        except Exception as e:
            print(f'ERROR decrypting token: {e}')
            return

        dummy = EventData(
            event_name='Purchase',
            event_time=int(time.time()),
            event_source_url='https://test.example.com/order/diag-test'
        )

        payload = _build_tiktok_payload(client, [dummy])
        print('\nPayload being sent to TikTok:')
        print(json.dumps(payload, indent=2))

        print('\nCalling TikTok API...')
        result = await send_to_tiktok(client, [dummy])
        print(f'\nTikTok API Result: {result}')

        if result and result.get('code') == 0:
            print('\n✅ TikTok event sent SUCCESSFULLY!')
            print('👉 Check your TikTok Events Manager -> Test Events tab now.')
        else:
            print(f'\n❌ TikTok returned error: {result}')


asyncio.run(run())
