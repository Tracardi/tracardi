import logging
from typing import Tuple, Optional

from tracardi.config import tracardi
from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_to_event_mapping import map_to_event_mapping_table, \
    map_to_event_mapping
from tracardi.service.storage.mysql.schema.table import EventMappingTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventMappingService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(EventMappingTable, search, limit, offset)

    async def load_by_id(self, event_mapping_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(EventMappingTable, primary_id=event_mapping_id)

    async def delete_by_id(self, event_mapping_id: str) -> Tuple[bool, Optional[EventTypeMetadata]]:
        return await self._delete_by_id_in_deployment_mode(EventMappingTable, map_to_event_mapping, primary_id=event_mapping_id)

    async def insert(self, event_type_metadata: EventTypeMetadata):
        return await self._replace(EventMappingTable, map_to_event_mapping_table(event_type_metadata))

    async def load_by_event_type(self, event_type: str, only_enabled: bool = True) -> SelectResult:
        if only_enabled:
            where = where_tenant_and_mode_context(
                EventMappingTable,
                EventMappingTable.event_type == event_type,
                EventMappingTable.enabled == only_enabled
            )
        else:
            where = where_tenant_and_mode_context(
                EventMappingTable,
                EventMappingTable.event_type == event_type
            )

        return await self._select_query(EventMappingTable,
                                        where=where,
                                        order_by=EventMappingTable.name
                                        )

    async def load_by_event_type_id(self, event_type_id: str, only_enabled: bool = True) -> SelectResult:
        if only_enabled:
            where = where_tenant_and_mode_context(
                EventMappingTable,
                EventMappingTable.event_type == event_type_id,
                EventMappingTable.enabled == only_enabled
            )
        else:
            where = where_tenant_and_mode_context(
                EventMappingTable,
                EventMappingTable.event_type == event_type_id
            )

        return await self._select_query(EventMappingTable,
                                        where=where,
                                        order_by=EventMappingTable.name,
                                        one_record=True
                                        )