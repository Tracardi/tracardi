import logging

from tracardi.config import tracardi
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_reshaping_mapping import map_to_event_reshaping_table
from tracardi.service.storage.mysql.schema.table import EventReshapingTable
from tracardi.service.storage.mysql.service.table_service import TableService, where_tenant_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventReshapingService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        if search:
            where = where_tenant_context(
                EventReshapingTable,
                EventReshapingTable.name.like(f'%{search}%')
            )
        else:
            where = where_tenant_context(EventReshapingTable)

        return await self._select_query(EventReshapingTable,
                                        where=where,
                                        order_by=EventReshapingTable.name,
                                        limit=limit,
                                        offset=offset)

    async def load_by_id(self, event_reshaping_id: str) -> SelectResult:
        return await self._load_by_id(EventReshapingTable, primary_id=event_reshaping_id)

    async def delete_by_id(self, event_reshaping_id: str) -> str:
        return await self._delete_by_id(EventReshapingTable, primary_id=event_reshaping_id)

    async def insert(self, event_reshaping: EventReshapingSchema):
        return await self._replace(EventReshapingTable, map_to_event_reshaping_table(event_reshaping))


    async def load_by_event_type(self, event_type: str, only_enabled: bool = True):
        if only_enabled:
            where = where_tenant_context(
                EventReshapingTable,
                EventReshapingTable.event_type == event_type,
                EventReshapingTable.enabled == only_enabled
            )
        else:
            where = where_tenant_context(
                EventReshapingTable,
                EventReshapingTable.event_type == event_type
            )

        return await self._select_query(EventReshapingTable,
                                        where=where,
                                        order_by=EventReshapingTable.name)