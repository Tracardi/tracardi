import logging

from tracardi.config import tracardi
from tracardi.domain.consent_type import ConsentType
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.consent_type_mapping import map_to_consent_type_table
from tracardi.service.storage.mysql.schema.table import ConsentTypeTable
from tracardi.service.storage.mysql.service.table_service import TableService, where_tenant_and_mode_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class ConsentTypeService(TableService):

    async def load_all(self, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all(ConsentTypeTable, limit=limit, offset=offset)

    async def load_by_id(self, consent_type_id: str) -> SelectResult:
        return await self._load_by_id(ConsentTypeTable, primary_id=consent_type_id)

    async def delete_by_id(self, consent_type_id: str) -> str:
        return await self._delete_by_id(ConsentTypeTable, primary_id=consent_type_id)

    async def insert(self, consent_type: ConsentType):
        return await self._insert_if_none(ConsentTypeTable, map_to_consent_type_table(consent_type))


    async def load_keys(self, limit: int = None, offset: int = None) -> SelectResult:
        where = where_tenant_and_mode_context(
            ConsentTypeTable,
            ConsentTypeTable.enabled == True
        )

        return await self._select_query(
            ConsentTypeTable,
            columns=[ConsentTypeTable.id],
            where=where,
            limit=limit,
            offset=offset,
            distinct=True
        )

