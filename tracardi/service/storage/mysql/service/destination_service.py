import logging
from tracardi.config import tracardi
from tracardi.domain.destination import Destination
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.setup.setup_resources import get_resource_types
from tracardi.service.storage.mysql.mapping.destination_mapping import map_to_destination_table
from tracardi.service.storage.mysql.schema.table import DestinationTable
from tracardi.service.storage.mysql.service.table_service import TableService, where_tenant_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class DestinationService(TableService):


    async def load_all(self) -> SelectResult:
        return await self._load_all(DestinationTable)

    async def load_by_id(self, destination_id: str) -> SelectResult:
        return await self._load_by_id(DestinationTable, primary_id=destination_id)

    async def delete_by_id(self, destination_id: str) -> str:
        return await self._delete_by_id(DestinationTable, primary_id=destination_id)

    async def insert(self, destination: Destination):
        return await self._replace(DestinationTable, map_to_destination_table(destination))


    # Custom

    async def load_event_destinations(self, event_type: str, source_id: str) -> SelectResult:
        where = where_tenant_context(
            DestinationTable,
            DestinationTable.enabled == True,
            DestinationTable.on_profile_change_only == False,
            DestinationTable.source_id == source_id,
            DestinationTable.event_type_id == event_type,
        )
        return await self._query(DestinationTable, where)

    async def load_profile_destinations(self) -> SelectResult:
        where = where_tenant_context(
            DestinationTable,
            DestinationTable.enabled == True,
            DestinationTable.on_profile_change_only == True
        )
        return await self._query(DestinationTable, where)

    @staticmethod
    def get_destination_types():
        resource_types = get_resource_types()
        for resource_type in resource_types:
            if resource_type.destination is not None:
                yield resource_type.destination.package, resource_type.dict()
                

    async def filter(self, text: str, start: int=None, limit: int=None) -> SelectResult:
        if text:
            where = where_tenant_context(
                DestinationTable,
                DestinationTable.name.like(f"%{text}%")
            )
        else:
            where = where_tenant_context(DestinationTable)
        return await self._query(DestinationTable, where, order_by=DestinationTable.name, limit=limit, offset=start)
                
