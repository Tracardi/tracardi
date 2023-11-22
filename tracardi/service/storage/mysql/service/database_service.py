from sqlalchemy import text

from tracardi.config import mysql
from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
from tracardi.service.storage.mysql.schema.table import Base


class DatabaseService:

    def __init__(self):
        self.client = AsyncMySqlEngine()

    async def _create_tables(self):
        engine = self.client.get_engine_for_database()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()
        await engine.dispose()

    async def _create_database(self):
        engine = self.client.get_engine()
        async with engine.connect() as conn:
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {mysql.mysql_database}"))
            await conn.commit()
        await engine.dispose()

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