import logging

from tracardi.config import tracardi
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_reshaping_mapping import map_to_event_reshaping_table
from tracardi.service.storage.mysql.schema.table import EventReshapingTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventReshapingService(TableService):

    async def load_all(self) -> SelectResult:
        return await self._load_all(EventReshapingTable)

    async def load_by_id(self, event_reshaping_id: str) -> SelectResult:
        return await self._load_by_id(EventReshapingTable, primary_id=event_reshaping_id)

    async def delete_by_id(self, event_reshaping_id: str) -> str:
        return await self._delete_by_id(EventReshapingTable, primary_id=event_reshaping_id)

    async def insert(self, event_reshaping: EventReshapingSchema):
        return await self._insert_if_none(EventReshapingTable, map_to_event_reshaping_table(event_reshaping))
