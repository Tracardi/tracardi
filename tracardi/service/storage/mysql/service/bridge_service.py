import logging

from typing import List

from tracardi.config import tracardi
from tracardi.domain.bridge import Bridge
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.bridge_mapping import map_to_bridge_table
from tracardi.service.storage.mysql.schema.table import BridgeTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class BridgeService(TableService):

    async def load_all(self) -> SelectResult:
        return await self.__load_all(BridgeTable, server_context=False)

    async def load_by_id(self, plugin_id: str) -> SelectResult:
        return await self._load_by_id(BridgeTable, primary_id=plugin_id, server_context=False)

    async def delete_by_id(self, bridge_id: str) -> bool:
        return await self._delete_by_id(BridgeTable, primary_id=bridge_id, server_context=False)


    async def insert(self, bridge: Bridge):
        return await self._insert_if_none(BridgeTable, map_to_bridge_table(bridge), server_context=False)

    # Custom

    @staticmethod
    async def bootstrap(default_bridges: List[Bridge]):
        bs = BridgeService()
        for bridge in default_bridges:
            await bs.insert(bridge)
            logger.info(f"Bridge {bridge.name} installed.")
