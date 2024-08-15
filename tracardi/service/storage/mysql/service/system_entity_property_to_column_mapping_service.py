from typing import List, Generator

from sqlalchemy import select, and_

from com_tracardi.domain.object_mapping import ObjectMapping
from tracardi.context import get_context
from tracardi.domain.system_entity_mapping import SystemEntityPropertyToColumn
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.decorators.function_memory_cache import async_cache_for
from tracardi.service.storage.mysql.mapping.system_entity_property_to_column_mapping import \
    map_to_system_entity_property_to_column_table
from tracardi.service.storage.mysql.schema.table import SystemEntityPropertyToColumnMappingTable, \
    SystemEntityPropertyTable, SystemEntityTableColumnTable
from tracardi.service.storage.mysql.service.table_service import TableService

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

    async def _load_by_type(self, entity_type: str, only_enabled: bool = True) -> Generator[ObjectMapping, None, None]:
        local_session = self.client.get_session(self.engine)
        context = get_context()
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                sql = select(
                    SystemEntityPropertyTable,
                    SystemEntityPropertyToColumnMappingTable,
                    SystemEntityTableColumnTable
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
                result = await session.execute(sql)
                for object, cross, storage in result.all():  # type: SystemEntityPropertyTable, SystemEntityPropertyToColumnMappingTable, SystemEntityTableColumnTable
                    yield ObjectMapping(
                        database=storage.database,
                        table=storage.table,
                        column=storage.column,
                        column_type=storage.type,
                        entity=object.entity,
                        property=object.property,
                        default=object.default,
                        value_type=object.type,
                    )

    @async_cache_for(60*15)
    async def load_by_type(self, entity_type: str, only_enabled: bool = True) -> List[ObjectMapping]:
        return [item async for item in self._load_by_type(entity_type, only_enabled)]
