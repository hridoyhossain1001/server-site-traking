import asyncio
import logging
from sqlalchemy import text
from app.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    logger.info("Connecting to database to add COD automation columns...")
    async with engine.begin() as conn:
        # Add auto_confirm_days
        logger.info("Adding column auto_confirm_days...")
        await conn.execute(text("ALTER TABLE clients ADD COLUMN IF NOT EXISTS auto_confirm_days INTEGER DEFAULT 0 NOT NULL;"))

        # Add auto_confirm_status
        logger.info("Adding column auto_confirm_status...")
        await conn.execute(text("ALTER TABLE clients ADD COLUMN IF NOT EXISTS auto_confirm_status VARCHAR(50) DEFAULT 'completed';"))

    logger.info("Database migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
