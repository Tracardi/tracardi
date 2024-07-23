import logging
from typing import Optional, Tuple

from tracardi.config import tracardi
from tracardi.domain.resource import Resource
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.resource_mapping import map_to_resource_table, map_to_resource
from tracardi.service.storage.mysql.schema.table import ResourceTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context, sql_functions

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class ResourceService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(ResourceTable, search, limit, offset)

    async def load_by_id(self, resource_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(ResourceTable, primary_id=resource_id)

    async def delete_by_id(self, resource_id: str) -> Tuple[bool, Optional[Resource]]:
        return await self._delete_by_id_in_deployment_mode(ResourceTable, map_to_resource,
                                                           primary_id=resource_id)

    async def insert(self, resource: Resource):
        return await self._replace(ResourceTable, map_to_resource_table(resource))

    async def load_enabled_by_tag(self, tag: str):
        where = where_tenant_and_mode_context(
            ResourceTable,
            sql_functions().find_in_set(tag, ResourceTable.tags) > 0,
            ResourceTable.enabled == True
        )

        return await self._select_in_deployment_mode(
            ResourceTable,
            where=where
        )

    async def load_resource_with_destinations(self) -> SelectResult:
        where = where_tenant_and_mode_context(
            ResourceTable,
            ResourceTable.destination.isnot(None)
        )

        return await self._select_in_deployment_mode(
            ResourceTable,
            where=where
        )
