import logging
from typing import Optional, Tuple

from tracardi.config import tracardi
from tracardi.domain.identification_point import IdentificationPoint
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.identification_point_mapping import map_to_identification_point_table, \
    map_to_identification_point
from tracardi.service.storage.mysql.schema.table import IdentificationPointTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class IdentificationPointService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(IdentificationPointTable, search, limit, offset)

    async def load_by_id(self, identification_point_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(IdentificationPointTable, primary_id=identification_point_id)

    async def delete_by_id(self, identification_point_id: str) -> Tuple[bool, Optional[IdentificationPoint]]:
        return await self._delete_by_id_in_deployment_mode(IdentificationPointTable, map_to_identification_point,
                                                           primary_id=identification_point_id)


    async def insert(self, identification_point: IdentificationPoint):
        return await self._replace(IdentificationPointTable, map_to_identification_point_table(identification_point))

    async def load_enabled(self, limit: int = 100) -> SelectResult:
        where = where_tenant_and_mode_context(
            IdentificationPointTable,
            IdentificationPointTable.enabled == True
        )
        return await self._select_in_deployment_mode(
            IdentificationPointTable,
            where=where,
            limit=limit,
            offset=0
        )

    async def load_by_event_type(self, event_type_id: str) -> SelectResult:
        where = where_tenant_and_mode_context(
            IdentificationPointTable,
            IdentificationPointTable.event_type_id == event_type_id
        )
        return await self._select_in_deployment_mode(
            IdentificationPointTable,
            where=where
        )
