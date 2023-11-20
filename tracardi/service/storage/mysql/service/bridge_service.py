import logging

from typing import List

from tracardi.config import tracardi, mysql
from tracardi.domain.bridge import Bridge
from tracardi.exceptions.log_handler import log_handler
from sqlalchemy import text

from tracardi.service.storage.mysql.schema.table import Base
from tracardi.service.storage.mysql.mapping.bridge_mapping import map_to_table
from tracardi.service.storage.mysql.schema.table import BridgeTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class BridgeService(TableService):

    async def load_all(self) -> SelectResult:
        return await self._load_all(BridgeTable)

    async def load_by_id(self, plugin_id: str) -> SelectResult:
        return await self._load_by_id(BridgeTable, primary_id=plugin_id)

    async def delete(self, bridge_id: str) -> str:
        return await self._delete(BridgeTable, primary_id=bridge_id)


    async def insert(self, bridge: Bridge):
        return await self._insert_if_none(BridgeTable, map_to_table(bridge))

    # Custom

    async def _create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def _create_database(self):
        async_engine = self.client.get_engine()
        async with async_engine.connect() as conn:
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {mysql.mysql_database}"))
            await conn.commit()
        await async_engine.dispose()

    async def bootstrap(self, default_bridges: List[Bridge]):

        # Connect to the database
        await self._create_database()

        # Create a new async engine instance with the database selected
        await self._create_tables()

        bs = BridgeService()
        for bridge in default_bridges:
            await bs.insert(bridge)
            logger.info(f"Bridge {bridge.name} installed.")
