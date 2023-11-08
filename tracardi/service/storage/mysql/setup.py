import asyncio
from sqlalchemy import text

from tracardi.domain.bridge import Bridge
from tracardi.service.storage.mysql.bootstrap.bridge import bridge_init
from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
from tracardi.service.storage.mysql.mapping.bridge import map_to_object
from tracardi.service.storage.mysql.orm import BridgeService
from tracardi.service.storage.mysql.table import Base

# Replace the user, password, host, and the database name with your credentials and desired database name
ASYNC_DB_URL = "mysql+aiomysql://root:root@localhost/"

# The name of the database you want to create
DATABASE_NAME = "tracardi"


# Async function to create tables
async def create_tables(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Async function to create a database
async def create_database(async_engine):
    async with async_engine.connect() as conn:
        await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
        await conn.commit()


async def bootstrap():
    engine = AsyncMySqlEngine()

    # Create an async engine instance
    async_engine = engine.get_engine()

    # Connect to the database
    await create_database(async_engine)

    # Dispose the engine to avoid any connection issues
    await async_engine.dispose()

    # Create a new async engine instance with the database selected
    async_engine_with_db = engine.get_engine_for_database(DATABASE_NAME)

    await create_tables(async_engine_with_db)

    # Dispose the engine with the database as it's not needed anymore
    await async_engine_with_db.dispose()

    # bs = BridgeService(DATABASE_NAME)
    # bs.load_all().:
    #     print(map_to_object(x))

    # print(await bridge_init(DATABASE_NAME))


# Run the async function using asyncio.run() if using Python 3.7+
asyncio.run(bootstrap())
