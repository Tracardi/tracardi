import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

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
    # Create an async engine instance
    async_engine = create_async_engine(ASYNC_DB_URL, echo=True)

    # Connect to the database
    await create_database(async_engine)

    # Dispose the engine to avoid any connection issues
    await async_engine.dispose()

    # Create a new async engine instance with the database selected
    async_engine_with_db = create_async_engine(f"{ASYNC_DB_URL}{DATABASE_NAME}", echo=True)

    await create_tables(async_engine_with_db)

    # Dispose the engine with the database as it's not needed anymore
    await async_engine_with_db.dispose()


# Run the async function using asyncio.run() if using Python 3.7+
asyncio.run(bootstrap())
