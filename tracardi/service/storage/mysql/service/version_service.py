from typing import Optional

import logging
from tracardi.config import tracardi
from tracardi.domain.version import Version
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.version_mapping import map_to_version_table, map_to_version
from tracardi.service.storage.mysql.schema.table import VersionTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.user_service import _where_with_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

# --------------------------------------------------------
# This Service Runs in Production and None-Production Mode
# It is PRODUCTION CONTEXT-LESS
# --------------------------------------------------------

class VersionService(TableService):

    async def load_all(self, limit: int = None, offset: int = None) -> SelectResult:
        where = _where_with_context()

        return await self._select_query(VersionTable,
                                        where=where,
                                        limit=limit,
                                        offset=offset)

    async def upsert(self, version: Version):
        return await self._replace(VersionTable, map_to_version_table(version))

    async def load_by_version(self, version: str) -> Optional[Version]:
        where = _where_with_context(  # tenant only mode
            VersionTable.api_version == version
        )

        records = await self._select_query(VersionTable, where=where)

        if not records.exists():
            return None

        return records.map_first_to_object(map_to_version)
