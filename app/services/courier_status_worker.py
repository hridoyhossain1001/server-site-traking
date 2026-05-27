import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select, or_, and_

from app.database import AsyncSessionLocal
from app.models.client import Client
from app.models.courier_order import CourierOrder
from app.routers.courier_webhook import process_courier_status_change
from app.security import decrypt_token
from app.services.courier_service import CourierService

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 1800 # 30 minutes fallback check

async def poll_active_courier_orders() -> None:
    logger.info("Starting periodic courier status sync loop...")
    
    async with AsyncSessionLocal() as db:
        # Find all orders that are not finalized (i.e. not delivered, returned, or cancelled)
        result = await db.execute(
            select(CourierOrder).where(
                CourierOrder.courier_status.in_(["pending", "picked", "in_transit"])
            )
        )
        active_orders = result.scalars().all()
        
        if not active_orders:
            logger.info("No active courier orders to sync.")
            return
            
        logger.info(f"Found {len(active_orders)} active courier orders to sync.")
        
        for order in active_orders:
            try:
                # Load client
                client_res = await db.execute(select(Client).where(Client.id == order.client_id))
                client = client_res.scalar_one_or_none()
                if not client:
                    continue
                    
                new_status = None
                
                # Check based on provider
                if order.courier_provider == "steadfast":
                    if client.steadfast_api_key and client.steadfast_secret_key:
                        api_key = client.steadfast_api_key
                        secret_key = decrypt_token(client.steadfast_secret_key)
                        
                        new_status = await CourierService.check_steadfast_status(
                            api_key=api_key,
                            secret_key=secret_key,
                            tracking_code=order.courier_tracking_id
                        )
                        
                elif order.courier_provider == "pathao":
                    if client.pathao_api_key and client.pathao_secret_key and client.pathao_store_id:
                        try:
                            client_id, email = client.pathao_api_key.split("|", 1)
                            decrypted_secret_pass = decrypt_token(client.pathao_secret_key)
                            client_secret, password = decrypted_secret_pass.split("|", 1)
                            
                            new_status = await CourierService.check_pathao_status(
                                client_id=client_id,
                                client_secret=client_secret,
                                email=email,
                                password=password,
                                consignment_id=order.courier_order_id
                            )
                        except ValueError:
                            logger.error(f"Pathao credential format incorrect for client {client.name}")
                            
                if new_status:
                    logger.info(f"Syncing status for order {order.order_id}: {order.courier_status} -> {new_status}")
                    await process_courier_status_change(db, order, new_status)
                    await db.commit()
                
            except Exception as e:
                logger.error(f"Error syncing status for courier order {order.id}: {e}")
                await db.rollback()

async def poll_courier_statuses_forever() -> None:
    """Background loop to sync courier statuses forever."""
    logger.info("Courier status worker initialized.")
    # Wait 60s after startup to run the first check
    await asyncio.sleep(60)
    
    while True:
        try:
            await poll_active_courier_orders()
        except Exception as e:
            logger.error(f"Error in courier status poll loop: {e}")
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
