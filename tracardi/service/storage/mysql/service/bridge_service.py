from typing import List

from tracardi.domain.bridge import Bridge
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.mysql.mapping.bridge_mapping import map_to_bridge_table
from tracardi.service.storage.mysql.schema.table import BridgeTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = get_logger(__name__)


class BridgeService(TableService):

    async def load_all(self) -> SelectResult:
        return await self._base_load_all(BridgeTable, server_context=False)

    async def load_by_id(self, plugin_id: str) -> SelectResult:
        return await self._load_by_id(BridgeTable, primary_id=plugin_id, server_context=False)

    async def delete_by_id(self, bridge_id: str) -> tuple:
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
