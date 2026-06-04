import asyncio
import sys
import os
from pathlib import Path

from alembic import command
from alembic.config import Config

# Add parent directory to path so we can import app
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from app.database import engine, Base

# Import all models to ensure they are registered in metadata
import app.models  # noqa: F401


async def create_tables():
    print("Creating all database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created successfully!")


def stamp_schema():
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    command.stamp(config, "head")
    print("Database schema stamped with the current Alembic head.")


if __name__ == "__main__":
    asyncio.run(create_tables())
    stamp_schema()
