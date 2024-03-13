from typing import Optional, Tuple

import logging

from tracardi.config import tracardi
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_to_profile_mapping import map_to_event_to_profile_table, \
    map_to_event_to_profile
from tracardi.service.storage.mysql.schema.table import EventToProfileMappingTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventToProfileMappingService(TableService):

    async def load_all(self, search: Optional[str] = None, limit: Optional[int] = None, offset: Optional[int] = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(EventToProfileMappingTable, search, limit, offset)

    async def load_by_id(self, mapping_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(EventToProfileMappingTable, primary_id=mapping_id)

    async def delete_by_id(self, mapping_id: str) -> Tuple[bool, Optional[EventToProfile]]:
        return await self._delete_by_id_in_deployment_mode(EventToProfileMappingTable, map_to_event_to_profile, primary_id=mapping_id)

    async def insert(self, mapping: EventToProfile):
        return await self._replace(EventToProfileMappingTable, map_to_event_to_profile_table(mapping))

    async def load_by_type(self, event_type: str, enabled_only: bool = False) -> SelectResult:
        if enabled_only:
            where = where_tenant_and_mode_context(
                    EventToProfileMappingTable,
                    EventToProfileMappingTable.event_type_id == event_type,
                    EventToProfileMappingTable.enabled == True
                )
        else:
            where = where_tenant_and_mode_context(
                EventToProfileMappingTable,
                EventToProfileMappingTable.event_type_id == event_type
            )

        return await self._select_in_deployment_mode(
            EventToProfileMappingTable,
            where=where
        )
