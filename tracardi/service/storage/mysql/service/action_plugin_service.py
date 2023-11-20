import logging

from tracardi.config import tracardi
from tracardi.domain.flow_action_plugin import FlowActionPlugin
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.plugin_mapping import map_to_table
from tracardi.service.storage.mysql.schema.table import PluginTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.utils.select_result import SelectResult


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

class ActionPluginService(TableService):

    async def load_all(self) -> SelectResult:
        return await self._load_all(PluginTable)

    async def load_by_id(self, plugin_id: str) -> SelectResult:
        return await self._load_by_id(PluginTable, primary_id=plugin_id)

    async def insert(self, plugin: FlowActionPlugin) -> str:
        return await self._replace(PluginTable, map_to_table(plugin))

    async def update(self, data: dict, plugin_id: str):
        return await self._update(PluginTable, primary_id=plugin_id, new_data=data)

    async def delete(self, plugin_id):
        return await self._delete(PluginTable, primary_id=plugin_id)

    async def filter(self, purpose: str):
        return await self._field_filter(PluginTable, field=PluginTable.plugin_metadata_purpose, value=purpose)
