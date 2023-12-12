import logging

from tracardi.config import tracardi
from tracardi.domain.resource import Resource
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.resource_mapping import map_to_resource_table
from tracardi.service.storage.mysql.schema.table import ResourceTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService, where_tenant_context, sql_functions

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class ResourceService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        where = None
        if search:
            where = where_tenant_context(
                ResourceTable,
                ResourceTable.name.like(f'%{search}%')
            )

        return await self._select_query(ResourceTable,
                                        where=where,
                                        order_by=ResourceTable.name,
                                        limit=limit,
                                        offset=offset)

    async def load_by_id(self, resource_id: str) -> SelectResult:
        return await self._load_by_id(ResourceTable, primary_id=resource_id)

    async def delete_by_id(self, resource_id: str) -> str:
        return await self._delete_by_id(ResourceTable, primary_id=resource_id)

    async def insert(self, resource: Resource):
        return await self._replace(ResourceTable, map_to_resource_table(resource))


    async def load_by_tag(self, tag: str):

        where = where_tenant_context(
            ResourceTable,
            sql_functions().find_in_set(tag, ResourceTable.tags)>0
        )

        return await self._select_query(
            ResourceTable,
            where=where
        )


    async def load_resource_with_destinations(self) -> SelectResult:
        where = where_tenant_context(
            ResourceTable,
            ResourceTable.destination.isnot(None)
        )

        return await self._select_query(
            ResourceTable,
            where=where
        )