from typing import Tuple, Optional
from tracardi.domain.consent_type import ConsentType
from tracardi.service.storage.mysql.mapping.consent_type_mapping import map_to_consent_type_table, map_to_consent_type
from tracardi.service.storage.mysql.schema.table import ConsentTypeTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult


class ConsentTypeService(TableService):

    async def load_all(self, search: Optional[str]=None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(ConsentTypeTable, search, limit, offset)

    async def load_by_id(self, consent_type_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(ConsentTypeTable, primary_id=consent_type_id)

    async def delete_by_id(self, consent_type_id: str) -> Tuple[bool, Optional[ConsentType]]:
        return await self._delete_by_id_in_deployment_mode(ConsentTypeTable,
                                                           map_to_consent_type,
                                                           primary_id=consent_type_id)

    async def insert(self, consent_type: ConsentType):
        return await self._replace(ConsentTypeTable, map_to_consent_type_table(consent_type))

    async def load_enabled(self, limit: int = None, offset: int = None) -> SelectResult:
        where = where_tenant_and_mode_context(
            ConsentTypeTable,
            ConsentTypeTable.enabled == True
        )

        return await self._select_in_deployment_mode(
            ConsentTypeTable,
            where=where,
            limit=limit,
            offset=offset,
            distinct=True
        )

