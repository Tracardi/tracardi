You are a programmer, your task is to write Python tests in pytest for a service class that interacts with a MySQL database.
This service class utilizes SQLAlchemy for database operations, employing both table objects and domain objects to read
and write data. Here's a structured example to guide you through this process. USe this example to write test for the service class:

Check this table class:

```python
class BridgeTable(Base):
    __tablename__ = 'bridge'

    id = Column(String(40))  # 'keyword' with ignore_above maps to VARCHAR with length
    tenant = Column(String(40))
    name = Column(String(64), index=True)  # 'text' type in ES maps to VARCHAR(255) in MySQL
    description = Column(Text)  # 'text' type in ES maps to VARCHAR(255) in MySQL
    type = Column(String(48))  # 'keyword' type in ES maps to VARCHAR(255) in MySQL
    config = Column(JSON)  # 'object' type in ES with 'enabled' false maps to JSON in MySQL
    form = Column(JSON)  # 'object' type in ES with 'enabled' false maps to JSON in MySQL
    manual = Column(Text, nullable=True)  # 'keyword' type in ES with 'index' false maps to VARCHAR(255) in MySQL

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant'),
    )
```

Check the domain object:

```python

class Bridge(NamedEntity):
    description: Optional[str] = ""
    type: str
    config: Optional[dict] = {}
    form: Optional[Form] = None
    manual: Optional[str] = None
```

This is the example of a service class dependency:

```python
from typing import List
from tracardi.domain.bridge import Bridge
from tracardi.service.storage.mysql.mapping.bridge_mapping import map_to_bridge_table
from tracardi.service.storage.mysql.schema.table import BridgeTable
from typing import Optional, Type, Any

from sqlalchemy.dialects.mysql import insert
from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
from sqlalchemy.future import select
from sqlalchemy import and_, delete, inspect, update, Column, Table, text, Select
from sqlalchemy.sql import func


from tracardi.service.storage.mysql.schema.table import Base, tenant_only_context_filter
from tracardi.service.storage.mysql.schema.table import tenant_and_mode_context_filter
from tracardi.service.storage.mysql.utils.select_result import SelectResult

def where_tenant_and_mode_context(table, *clauses):
    return and_(tenant_and_mode_context_filter(table), *clauses)


def where_only_tenant_context(table, *clauses):
    return and_(tenant_only_context_filter(table), *clauses)


def sql_functions():
    return func


def where_with_context(table: Type[Base], server_context:bool, *clauses):
    return where_tenant_and_mode_context(
        table,
        *clauses
    ) if server_context else where_only_tenant_context(
        table,
        *clauses
    )

class TableService:

    def __init__(self, echo: bool=None):
        self.client = AsyncMySqlEngine(echo)
        self.engine = self.client.get_engine_for_database()

    async def exists(self, table_name: str) -> bool:
        local_session = self.client.get_session(self.engine)

        async with local_session() as session:
            async with session.begin():
                # Use a raw SQL query to check for table existence
                query = text(f"SHOW TABLES LIKE '{table_name}';")
                result = await session.execute(query)
                return result.scalar() is not None

    @staticmethod
    def _select_clause(table: Type[Base],
                       columns=None,
                       where=None,
                       order_by: Column=None,
                       limit:int=None,
                       offset:int=None,
                       distinct: bool = False) -> Select[Any]:



        if columns is not None:
            _select = select(*columns)
        else:
            _select = select(table)

        if distinct:
            _select = _select.distinct()

        if where is not None:
            _select = _select.where(where)

        if order_by is not None:
            _select = _select.order_by(order_by)

        if limit:
            _select = _select.limit(limit)

            if offset:
                _select = _select.offset(offset)

        return _select


    async def _load_all(self,
                        table: Type[Base],
                        columns=None,
                        order_by: Column = None,
                        limit: int = None,
                        offset: int = None,
                        distinct: bool = False,
                        server_context:bool=True) -> SelectResult:

        where = where_with_context(table, server_context)
            
        return await self._select_query(
            table,
            columns,
            where,
            order_by,
            limit,
            offset,
            distinct
        )

    async def _load_by_id(self, table: Type[Base], primary_id: str, server_context:bool=True) -> SelectResult:
        local_session = self.client.get_session(self.engine)

        where = where_with_context(table, server_context, table.id == primary_id)

        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                result = await session.execute(
                    select(table).where(where)
                )
                # Fetch all results
                return SelectResult(result.scalars().one_or_none())


    async def _field_filter(self, table: Type[Base], field: Column, value, server_context:bool=True) -> SelectResult:
        local_session = self.client.get_session(self.engine)

        where = where_with_context(table, server_context, field == value)

        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                result = await session.execute(select(table).where(where))
                # Fetch all results
                return SelectResult(result.scalars().all())

    async def _select_query(self,
                            table: Type[Base],
                            columns = None,
                            where = None,
                            order_by: Column=None,
                            limit:int=None,
                            offset:int=None,
                            distinct: bool = False,
                            one_record:bool=False) -> SelectResult:

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():

                _select = self._select_clause(table,
                                              columns,
                                              where,
                                              order_by,
                                              limit,
                                              offset,
                                              distinct)

                # Use SQLAlchemy core to perform an asynchronous query
                result = await session.execute(_select)
                # Fetch all results
                if one_record:
                    return SelectResult(result.scalars().one_or_none())
                return SelectResult(result.scalars().all())

    async def _insert(self, table: Type[Base]) -> Optional[str]:
        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                session.add(table)
                await session.commit()
                return table.id

    async def _update_by_id(self, table: Type[Base], primary_id: str, new_data: dict, server_context:bool=True) -> Optional[str]:
        local_session = self.client.get_session(self.engine)
        where = where_with_context(table, server_context,table.id == primary_id)

        async with local_session() as session:
            async with session.begin():
                stmt = (
                    update(table)
                    .where(where)
                    .values(**new_data)
                )
                await session.execute(stmt)
                await session.commit()
                return primary_id

    async def _update_query(self, table: Type[Base], where, new_data: dict):
        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                stmt = (
                    update(table)
                    .where(where)
                    .values(**new_data)
                )
                await session.execute(stmt)
                await session.commit()
                return None

    async def _replace(self, table: Type[Base], instance: Base) -> Optional[str]:
        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                # Convert the SQLAlchemy instance to a dictionary
                data = {c.key: getattr(instance, c.key) for c in inspect(instance).mapper.column_attrs}
                stmt = insert(table).values(**data)
                primary_keys = [key.name for key in inspect(table).primary_key]
                update_dict = {key: value for key, value in data.items() if key not in primary_keys}
                upsert_stmt = stmt.on_duplicate_key_update(**update_dict)
                await session.execute(upsert_stmt)
                await session.commit()

                # Assuming the primary key field is named 'id'
                return getattr(instance, 'id', None)

    async def _insert_if_none(self, table: Type[Base], data, server_context:bool=True) -> Optional[str]:

        local_session = self.client.get_session(self.engine)
        where = where_with_context(table, server_context,table.id == data.id)

        async with local_session() as session:
            async with session.begin():

                existing_row = (await session.execute(
                    select(table).where(where))).scalar()

                if existing_row is None:

                    # Add the new object to the session
                    session.add(data)

                    # The actual commit happens here
                    await session.commit()

                    # Return the id of the new record
                    return data.id

                return None


    async def _delete_by_id(self, table: Type[Base], primary_id: str, server_context:bool=True) -> str:

        where = where_with_context(table, server_context, table.id == primary_id)

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                await session.execute(
                    delete(table).where(where)
                )

                return primary_id

    async def _delete_query(self, table: Type[Base], where):

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                await session.execute(
                    delete(table).where(where)
                )
```

This is an example of service class.

```python
class BridgeService(TableService):

    async def load_all(self) -> SelectResult:
        return await self._load_all(BridgeTable, server_context=False)

    async def load_by_id(self, plugin_id: str) -> SelectResult:
        return await self._load_by_id(BridgeTable, primary_id=plugin_id, server_context=False)

    async def delete_by_id(self, bridge_id: str) -> str:
        return await self._delete_by_id(BridgeTable, primary_id=bridge_id, server_context=False)


    async def insert(self, bridge: Bridge):
        return await self._insert_if_none(BridgeTable, map_to_bridge_table(bridge), server_context=False)

    # Custom

    @staticmethod
    async def bootstrap(default_bridges: List[Bridge]):
        bs = BridgeService()
        for bridge in default_bridges:
            await bs.insert(bridge)
            logger.info(f"Bridge {bridge.name} installed.")

```

Here is an example of ready pytest TEST:

```python
import pytest
from uuid import uuid4

from tracardi.context import ServerContext, Context
from tracardi.domain.bridge import Bridge
from tracardi.service.storage.mysql.service.bridge_service import BridgeService


@pytest.mark.asyncio
# Test for loading all bridges
async def test_bridges():
    with ServerContext(Context(production=False)):  #  this is required
        service = BridgeService()
        bridge_id = uuid4().hex
        try:

            await service.insert(Bridge(
                id=bridge_id,
                name='test',
                type='rest'
            ))

            bridges = await service.load_all()
            assert bridges.has_multiple_records()
            bridge = await service.load_by_id(bridge_id)
            assert bridge.rows.id == bridge_id
        finally:  # Finally clean all the inserted data
            await service.delete_by_id(bridge_id)
            bridge = await service.load_by_id(bridge_id)
            assert bridge.exists() is False
```

Using the above examples your task is to write full functional pytest test that tests the `ConsentDataComplianceService` class.
The code of the class if below together with tabel class and domain class. Write pytest that writes tests for all
methods but in one test. Do not forget to put: with ServerContext(Context(production=True)): before all tests it is required.

```python
import logging

from tracardi.config import tracardi
from tracardi.domain.consent_field_compliance import EventDataCompliance
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_data_compliance_mapping import map_to_event_data_compliance_table
from tracardi.service.storage.mysql.schema.table import EventDataComplianceTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class ConsentDataComplianceService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        where = None
        if search:
            where = where_tenant_and_mode_context(
                EventDataComplianceTable,
                EventDataComplianceTable.name.like(f'%{search}%')
            )

        return await self._select_in_deployment_mode(EventDataComplianceTable,
                                        where=where,
                                        order_by=EventDataComplianceTable.name,
                                        limit=limit,
                                        offset=offset)

    async def load_by_id(self, data_compliance_id: str) -> SelectResult:
        return await self._load_by_id(EventDataComplianceTable, primary_id=data_compliance_id)

    async def delete_by_id(self, data_compliance_id: str) -> str:
        return await self._delete_by_id(EventDataComplianceTable, primary_id=data_compliance_id)

    async def insert(self, consent_data_compliance: EventDataCompliance):
        return await self._replace(EventDataComplianceTable,
                                   map_to_event_data_compliance_table(consent_data_compliance))

    async def load_by_event_type(self, event_type_id: str, enabled_only: bool = True):
        if enabled_only:
            where = where_tenant_and_mode_context(
                EventDataComplianceTable,
                EventDataComplianceTable.event_type_id == event_type_id,
                EventDataComplianceTable.enabled == enabled_only
            )
        else:
            where = where_tenant_and_mode_context(
                EventDataComplianceTable,
                EventDataComplianceTable.event_type_id == event_type_id
            )

        return await self._select_in_deployment_mode(EventDataComplianceTable,
                                        where=where,
                                        order_by=EventDataComplianceTable.name)



```

```python
from typing import List, Optional

from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.ref_value import RefValue


class ConsentFieldComplianceSetting(BaseModel):
    action: str  # Remove, Hash, Do nothing
    field: RefValue
    consents: List[NamedEntity]

    def get_consents(self) -> set:
        return {item.id for item in self.consents}

    def complies_to_consents(self, profile_consents: set) -> bool:
        required_consents = self.get_consents()
        return required_consents.intersection(profile_consents) == required_consents


class EventDataCompliance(Entity):
    name: str
    description: Optional[str] = ""
    event_type: NamedEntity
    settings: List[ConsentFieldComplianceSetting]  # Flattened ES field
    enabled: Optional[bool] = False

```

```python
class EventDataComplianceTable(Base):
    __tablename__ = 'event_data_compliance'

    id = Column(String(40))  # 'keyword' with 'ignore_above' 64
    name = Column(String(128))  # 'keyword' type in Elasticsearch
    description = Column(Text)  # 'keyword' type in Elasticsearch
    event_type_id = Column(String(40))  # Nested 'keyword' field named 'id'
    event_type_name = Column(String(64))  # Nested 'keyword' field named 'name'
    settings = Column(JSON)  # 'flattened' type in Elasticsearch maps to JSON
    enabled = Column(Boolean, default=False)   # 'boolean' type in Elasticsearch

    tenant = Column(String(40))  # Additional field for multi-tenancy
    production = Column(Boolean)  # Additional field for multi-tenancy

    __table_args__ = (
        PrimaryKeyConstraint('id', 'tenant', 'production'),
    )

```