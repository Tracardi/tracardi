import os
from sqlalchemy import text

from tracardi.config import starrocks
# from tracardi.service.storage.starrocks.schema.table import Base
from tracardi.service.storage.starrocks.engine import AsyncStarRocksEngine
from tracardi.service.utils.file import read_file

_local_dir = os.path.dirname(os.path.abspath(__file__))


class DatabaseService:

    def __init__(self):
        self.client = AsyncStarRocksEngine()

    # async def _create_tables(self):
    #     engine = self.client.get_engine_for_database()
    #     async with engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.create_all, checkfirst=False)
    #         await conn.commit()
    #     await engine.dispose()

    async def _create_tables(self):
        sql = read_file(os.path.join(_local_dir, "../schema/table.sql"))
        engine = self.client.get_engine_for_database()
        async with engine.connect() as conn:
            await conn.execute(text(sql))
            await conn.commit()
        await engine.dispose()

    async def _create_database(self):
        engine = self.client.get_engine()
        async with engine.connect() as conn:
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{starrocks.starrocks_database}`"))
            await conn.commit()
        await engine.dispose()

    async def query(self, query):
        engine = self.client.get_engine_for_database()
        async with engine.connect() as conn:
            result = await conn.execute(query)
            await conn.commit()
        await engine.dispose()
        return result

    async def exists(self, database_name: str) -> bool:
        engine = self.client.get_engine()
        async with engine.connect() as conn:
            result = await conn.execute(text(f"SHOW DATABASES LIKE '{database_name}';"))
            return result.fetchone() is not None

    async def bootstrap(self):
        # Connect to the database
        await self._create_database()

        # Create a new async engine instance with the database selected
        await self._create_tables()

    async def drop(self, database_name):
        engine = self.client.get_engine()
        async with engine.connect() as conn:
            await conn.execute(text(f"DROP DATABASE IF EXISTS `{database_name}`;"))
            await conn.commit()
