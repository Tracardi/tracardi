import logging

from tracardi.config import tracardi
from tracardi.domain.configuration import Configuration
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.configuration_mapping import map_to_configuration_table
from tracardi.service.storage.mysql.schema.table import ConfigurationTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_with_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

# --------------------------------------------------------
# This Service Runs in Production and None-Production Mode
# It is PRODUCTION CONTEXT-LESS
# --------------------------------------------------------

def _where_with_context(*clause):
    return where_with_context(
        ConfigurationTable,
        False,
        *clause
    )

class ConfigurationService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        if search:
            where = _where_with_context(
                ConfigurationTable.name.like(f'%{search}%')
            )
        else:
            where = _where_with_context()

        return await self._select_query(ConfigurationTable,
                                        where=where,
                                        order_by=ConfigurationTable.name,
                                        limit=limit,
                                        offset=offset)


    async def load_by_id(self, configuration_id: str) -> SelectResult:
        return await self._load_by_id(ConfigurationTable, primary_id=configuration_id, server_context=False)

    async def delete_by_id(self, configuration_id: str) -> tuple:
        return await self._delete_by_id(ConfigurationTable,
                                        primary_id=configuration_id,
                                        server_context=False)

    async def upsert(self, configuration: Configuration):
        return await self._replace(ConfigurationTable, map_to_configuration_table(configuration))


    