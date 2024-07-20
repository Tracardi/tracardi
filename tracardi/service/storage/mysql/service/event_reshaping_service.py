import logging
from typing import Optional, Tuple

from tracardi.config import tracardi
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_reshaping_mapping import map_to_event_reshaping_table, \
    map_to_event_reshaping
from tracardi.service.storage.mysql.schema.table import EventReshapingTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventReshapingService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(EventReshapingTable, search, limit, offset)

    async def load_by_id(self, event_reshaping_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(EventReshapingTable, primary_id=event_reshaping_id)

    async def delete_by_id(self, event_reshaping_id: str) -> Tuple[bool, Optional[EventReshapingSchema]]:
        return await self._delete_by_id_in_deployment_mode(EventReshapingTable, map_to_event_reshaping,
                                                           primary_id=event_reshaping_id)

    async def insert(self, event_reshaping: EventReshapingSchema):
        return await self._replace(EventReshapingTable, map_to_event_reshaping_table(event_reshaping))

    async def load_by_event_type(self, event_type: str, only_enabled: bool = True):
        if only_enabled:
            where = where_tenant_and_mode_context(
                EventReshapingTable,
                EventReshapingTable.event_type == event_type,
                EventReshapingTable.enabled == only_enabled
            )
        else:
            where = where_tenant_and_mode_context(
                EventReshapingTable,
                EventReshapingTable.event_type == event_type
            )

        return await self._select_in_deployment_mode(EventReshapingTable,
                                                     where=where,
                                                     order_by=EventReshapingTable.name)
