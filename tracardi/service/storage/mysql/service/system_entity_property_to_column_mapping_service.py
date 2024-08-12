from typing import List

from sqlalchemy import select, and_

from tracardi.context import get_context
from tracardi.domain.system_entity_mapping import SystemEntityPropertyToColumn
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.mysql.mapping.system_entity_property_to_column_mapping import \
    map_to_system_entity_property_to_column_table
from tracardi.service.storage.mysql.schema.table import SystemEntityPropertyToColumnMappingTable, \
    SystemEntityPropertyTable, SystemEntityTableColumnTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = get_logger(__name__)


class SystemEntityPropertyToColumnMapping(TableService):

    async def insert(self, mapping: SystemEntityPropertyToColumn):
        return await self._replace(
            SystemEntityPropertyToColumnMappingTable,
            map_to_system_entity_property_to_column_table(mapping))

    @staticmethod
    async def bootstrap(default_mappings: List[SystemEntityPropertyToColumn]):
        service = SystemEntityPropertyToColumnMapping()
        for mapping in default_mappings:
            await service.insert(mapping)
            logger.info(f"Table column {mapping.column_id} mapped to {mapping.property_id}.")

    async def load_by_type(self, entity_type: str, only_enabled: bool = True) -> SelectResult:
        local_session = self.client.get_session(self.engine)
        context = get_context()
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                sql = select(
                    SystemEntityPropertyTable,
                    SystemEntityTableColumnTable,
                    SystemEntityPropertyToColumnMappingTable
                ). \
                    join(SystemEntityPropertyToColumnMappingTable,
                         SystemEntityPropertyTable.id == SystemEntityPropertyToColumnMappingTable.property_id). \
                    join(SystemEntityTableColumnTable,
                         SystemEntityTableColumnTable.id == SystemEntityPropertyToColumnMappingTable.column_id). \
                    filter(
                    and_(
                        SystemEntityPropertyToColumnMappingTable.tenant == context.tenant,
                        SystemEntityPropertyTable.entity == entity_type
                    )
                )
                print(sql)
                result = await session.execute(sql)
                for a, b, c in result.all():
                    print("a", c.mode, a.id, a.property, b.id, b.table, b.column)

        # if only_enabled:
        #     where = where_tenant_and_mode_context(
        #         SystemEntityPropertyToColumnMappingTable,
        #         SystemEntityPropertyToColumnMappingTable.event_type == entity_type,
        #         EventMappingTable.enabled == only_enabled
        #     )
        # else:
        #     where = where_tenant_and_mode_context(
        #         EventMappingTable,
        #         EventMappingTable.event_type == entity_type
        #     )
        #
        # return await self._select_in_deployment_mode(EventMappingTable,
        #                                              where=where,
        #                                              order_by=EventMappingTable.name
        #                                              )
