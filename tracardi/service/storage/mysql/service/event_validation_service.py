import logging

from tracardi.config import tracardi
from tracardi.domain.event_validator import EventValidator
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_validation_mapping import map_to_event_validation_table
from tracardi.service.storage.mysql.schema.table import EventValidationTable
from tracardi.service.storage.mysql.service.table_service import TableService, where_tenant_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventValidationService(TableService):

    async def load_all(self, search:str = None, limit:int=None, offset:int=None) -> SelectResult:
        where = None
        if search:
            where = where_tenant_context(
                EventValidationTable,
                EventValidationTable.name.like(f'%{search}%')
            )

        return await self._select_query(EventValidationTable,
                                        where=where,
                                        order_by=EventValidationTable.name,
                                        limit=limit,
                                        offset=offset)

    async def load_by_id(self, event_validation_id: str) -> SelectResult:
        return await self._load_by_id(EventValidationTable, primary_id=event_validation_id)

    async def delete_by_id(self, event_validation_id: str) -> str:
        return await self._delete_by_id(EventValidationTable, primary_id=event_validation_id)

    async def insert(self, event_validation: EventValidator):
        return await self._replace(EventValidationTable, map_to_event_validation_table(event_validation))


    async def load_by_event_type(self, event_type: str, only_enabled: bool = True):
        if only_enabled:
            where = where_tenant_context(
                EventValidationTable,
                EventValidationTable.event_type == event_type,
                EventValidationTable.enabled == only_enabled
            )
        else:
            where = where_tenant_context(
                EventValidationTable,
                EventValidationTable.event_type == event_type
            )

        return await self._select_query(EventValidationTable,
                                        where=where,
                                        order_by=EventValidationTable.name)