import logging
from typing import Tuple, Optional

from tracardi.config import tracardi
from tracardi.domain.import_config import ImportConfig

from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.import_mapping import map_to_import_config_table, map_to_import_config
from tracardi.service.storage.mysql.schema.table import ImportTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class ImportService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(ImportTable, search, limit, offset)

    async def load_by_id(self, import_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(ImportTable, primary_id=import_id)

    async def delete_by_id(self, import_id: str) -> Tuple[bool, Optional[ImportConfig]]:
        return await self._delete_by_id_in_deployment_mode(ImportTable, map_to_import_config,
                                                           primary_id=import_id)

    async def insert(self, import_config: ImportConfig):
        table = map_to_import_config_table(import_config)
        return await self._replace(ImportTable, table)

