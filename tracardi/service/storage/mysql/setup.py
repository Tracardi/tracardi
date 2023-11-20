import logging

import asyncio
from sqlalchemy import text

from tracardi.config import mysql, tracardi
from tracardi.context import ServerContext, Context
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.bootstrap.bridge import os_default_bridges
from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
from tracardi.service.storage.mysql.mapping.bridge_mapping import map_to_bridge
from tracardi.service.storage.mysql.service.bridge_service import BridgeService
from tracardi.service.storage.mysql.schema.table import Base


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

# Async function to create tables
async def create_tables(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Async function to create a database
async def create_database(async_engine):
    async with async_engine.connect() as conn:
        await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {mysql.mysql_database}"))
        await conn.commit()


# async def bootstrap():
#     engine = AsyncMySqlEngine()
#
#     # # Create an async engine instance
#     async_engine = engine.get_engine()
#
#     # Connect to the database
#     await create_database(async_engine)
#
#     # Dispose the engine to avoid any connection issues
#     await async_engine.dispose()
#
#     # Create a new async engine instance with the database selected
#     async_engine_with_db = engine.get_engine_for_database()
#
#     await create_tables(async_engine_with_db)
#
#     # Dispose the engine with the database as it's not needed anymore
#     await async_engine_with_db.dispose()
#
#     bs = BridgeService()
#     for bridge in os_default_bridges:
#         await bs.insert(bridge)
#         logger.info(f"Bridge {bridge.name} installed.")
#
#     print(await bs.delete('3d8bb87e-28d1-4a38-b19c-d0c1fbb71e22'))
#
#     results = await bs.load_all()
#     for x in results.to_objects(map_to_bridge):
#         print(x)




async def main():
    with(ServerContext(Context(production=False, tenant="119a2"))):
        await bootstrap()


# Run the async function using asyncio.run() if using Python 3.7+
asyncio.run(main())
