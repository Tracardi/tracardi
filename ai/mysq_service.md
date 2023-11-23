This is a python code a service for Bridge. It runs standard CRUD functions.

```python
import logging

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
        return await self._load_all(BridgeTable)

    async def load_by_id(self, plugin_id: str) -> SelectResult:
        return await self._load_by_id(BridgeTable, primary_id=plugin_id)

    async def delete_by_id(self, bridge_id: str) -> str:
        return await self._delete_by_id(BridgeTable, primary_id=bridge_id)


    async def insert(self, bridge: Bridge):
        return await self._insert_if_none(BridgeTable, map_to_bridge_table(bridge))

```

rewrite it to be for current object `ConsentType`. Replace `Bridge` with current Object. And replace `BrideTable` to be `<current-object>Table`.
Notice that there is `map_to_bridge_table` function it should be named `map_to_<currnet-object>_table`, also `bridge_id` should be changed accordingly.

