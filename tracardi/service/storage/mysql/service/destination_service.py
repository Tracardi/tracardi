import logging
from sqlalchemy import or_
from typing import Tuple, Optional

from tracardi.config import tracardi
from tracardi.domain.destination import Destination
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.destination_mapping import map_to_destination_table, map_to_destination
from tracardi.service.storage.mysql.schema.table import DestinationTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class DestinationService(TableService):

    async def load_all(self, search: str, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(DestinationTable, search, limit, offset)

    async def load_by_id(self, destination_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(DestinationTable, primary_id=destination_id)

    async def delete_by_id(self, destination_id: str) -> Tuple[bool, Optional[Destination]]:
        return await self._delete_by_id_in_deployment_mode(DestinationTable, map_to_destination,
                                                           primary_id=destination_id)

    async def insert(self, destination: Destination):
        return await self._replace(DestinationTable, map_to_destination_table(destination))

    # Custom

    async def load_event_destinations(self, event_type: str, source_id: str) -> SelectResult:
        where = where_tenant_and_mode_context(
            DestinationTable,
            DestinationTable.enabled == True,
            DestinationTable.on_profile_change_only == False,
            DestinationTable.source_id == source_id,
            or_(DestinationTable.event_type_id == event_type, DestinationTable.event_type_id == None,
                DestinationTable.event_type_id == ""),
        )
        return await self._select_in_deployment_mode(DestinationTable, where=where)

    async def load_profile_destinations(self) -> SelectResult:
        where = where_tenant_and_mode_context(
            DestinationTable,
            DestinationTable.enabled == True,
            DestinationTable.on_profile_change_only == True
        )
        return await self._select_in_deployment_mode(DestinationTable, where=where)
