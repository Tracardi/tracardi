import logging

from tracardi.config import tracardi
from tracardi.domain.event_validator import EventValidator
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_validation_mapping import map_to_event_validation_table
from tracardi.service.storage.mysql.schema.table import EventValidationTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventValidationService(TableService):

    async def load_all(self) -> SelectResult:
        return await self._load_all(EventValidationTable)

    async def load_by_id(self, event_validation_id: str) -> SelectResult:
        return await self._load_by_id(EventValidationTable, primary_id=event_validation_id)

    async def delete_by_id(self, event_validation_id: str) -> str:
        return await self._delete_by_id(EventValidationTable, primary_id=event_validation_id)

    async def insert(self, event_validation: EventValidator):
        return await self._insert_if_none(EventValidationTable, map_to_event_validation_table(event_validation))
