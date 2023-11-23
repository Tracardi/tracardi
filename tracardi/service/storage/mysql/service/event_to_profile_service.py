import logging

from tracardi.config import tracardi
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_to_profile_mapping import map_to_event_to_profile_table
from tracardi.service.storage.mysql.schema.table import EventToProfileMappingTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventToProfileMappingService(TableService):

    async def load_all(self) -> SelectResult:
        return await self._load_all(EventToProfileMappingTable)

    async def load_by_id(self, mapping_id: str) -> SelectResult:
        return await self._load_by_id(EventToProfileMappingTable, primary_id=mapping_id)

    async def delete_by_id(self, mapping_id: str) -> str:
        return await self._delete_by_id(EventToProfileMappingTable, primary_id=mapping_id)

    async def insert(self, mapping: EventToProfile):
        return await self._insert_if_none(EventToProfileMappingTable, map_to_event_to_profile_table(mapping))
