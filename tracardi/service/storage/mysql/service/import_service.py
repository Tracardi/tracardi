import logging

from tracardi.config import tracardi
from tracardi.domain.import_config import ImportConfig

from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.import_mapping import map_to_import_config_table
from tracardi.service.storage.mysql.schema.table import ImportTable  # Adjusted for Import
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService, where_tenant_context

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class ImportService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        where = None
        if search:
            where = where_tenant_context(
                ImportTable,  # Adjusted for Import
                ImportTable.name.like(f'%{search}%')
            )

        return await self._select_query(ImportTable,
                                        where=where,
                                        order_by=ImportTable.name,
                                        limit=limit,
                                        offset=offset)

    async def load_by_id(self, import_id: str) -> SelectResult:
        return await self._load_by_id(ImportTable, primary_id=import_id)

    async def delete_by_id(self, import_id: str) -> str:
        return await self._delete_by_id(ImportTable, primary_id=import_id)

    async def insert(self, import_config: ImportConfig):
        table = map_to_import_config_table(import_config)
        return await self._replace(ImportTable, table)

