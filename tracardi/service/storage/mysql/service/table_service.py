from typing import Optional, Type, Any, Callable, Tuple, TypeVar

from sqlalchemy.dialects.mysql import insert

from tracardi.context import get_context
from tracardi.service.license import License, LICENSE
from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
from sqlalchemy import and_, inspect, update, Column, text
from sqlalchemy.sql import func


from tracardi.service.storage.mysql.schema.table import Base

if License.has_service(LICENSE):
    from com_tracardi.service.mysql.query_service import MysqlQuery
else:
    from tracardi.service.storage.mysql.query_service import MysqlQuery
from tracardi.service.storage.mysql.utils.select_result import SelectResult

T = TypeVar('T')

def tenant_only_context_filter(table: Type[Base]):
    context = get_context()
    return table.tenant == context.tenant

def custom_context_filter(table: Type[Base], tenant:str, production: bool, *clauses):
    def _wrapper():
        return and_(table.tenant == tenant, table.production == production, *clauses)
    return _wrapper

def tenant_and_mode_context_filter(table: Type[Base]):
    context = get_context()
    return and_(table.tenant == context.tenant, table.production == context.production)

def where_tenant_and_mode_context(table, *clauses) -> Callable:
    def _wrapper():
        return and_(tenant_and_mode_context_filter(table), *clauses)

    return _wrapper


def _where_only_tenant_context(table, *clauses) -> Callable:
    def _wrapper():
        return and_(tenant_only_context_filter(table), *clauses)
    return _wrapper

def sql_functions():
    return func


def where_with_context(table: Type[Base], server_context:bool, *clauses) -> Callable:
    return where_tenant_and_mode_context(
        table,
        *clauses
    ) if server_context else _where_only_tenant_context(
        table,
        *clauses
    )




class TableService:

    def __init__(self, echo: bool=False):
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
            distinct,
            in_deployment_mode=True
        )


    async def _load_by_id(self, table: Type[Base],
                          primary_id: str,
                          server_context:bool=True,
                          in_deployment_mode:bool=False
                          ) -> SelectResult:
        local_session = self.client.get_session(self.engine)

        where = where_with_context(table, server_context, table.id == primary_id)

        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                return await self._select_query(
                        table=table,
                        where=where,
                        one_record=True,
                        in_deployment_mode=in_deployment_mode
                    )


    async def _custom_load_by_id(self, table: Type[Base], primary_id: str, production:bool) -> SelectResult:

        context = get_context()
        where = custom_context_filter(table, context.tenant, production, table.id == primary_id)

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                return await self._select_query(
                        table=table,
                        where=where,
                        one_record=True
                    )


    async def _field_filter(self, table: Type[Base], field: Column, value, server_context:bool=True) -> SelectResult:
        local_session = self.client.get_session(self.engine)

        where = where_with_context(table, server_context, field == value)

        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                return await self._select_query(
                    table=table,
                    where=where,
                    one_record=False
                )

    async def _select_query(self,
                            table: Type[Base],
                            columns = None,
                            where: Callable = None,
                            order_by: Column=None,
                            limit:int=None,
                            offset:int=None,
                            distinct: bool = False,
                            one_record:bool=False,
                            in_deployment_mode:bool=False
                            ) -> SelectResult:

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():

                # Use SQLAlchemy core to perform an asynchronous query

                resource = MysqlQuery(session)

                if in_deployment_mode:
                    result = await resource.select_with_deployed_records(table,
                                                                         columns,
                                                                         where,
                                                                         order_by,
                                                                         limit,
                                                                         offset,
                                                                         distinct)
                else:
                    result = await resource.select(table,
                                                   columns,
                                                   where,
                                                   order_by,
                                                   limit,
                                                   offset,
                                                   distinct)

                # Fetch all results
                if one_record:
                    return SelectResult(result.one_or_none())
                return SelectResult(result.all())

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
                resource = MysqlQuery(session)
                await resource.update(table, new_data, where)
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

                resource = MysqlQuery(session)
                result = await resource.select(
                    table=table,
                    where=where)

                if result.empty():

                    # Add the new object to the session
                    resource.insert(data)

                    # The actual commit happens here
                    await session.commit()

                    # Return the id of the new record
                    return data.id

                return None


    async def _delete_by_id(self, table: Type[Base],
                            primary_id: str,
                            server_context:bool=True) -> bool:

        where = where_with_context(table, server_context, table.id == primary_id)

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                resource = MysqlQuery(session)
                await resource.delete(table, where)

        return True

    async def _delete_by_id_in_deployment_mode(self,
                                   table: Type[Base],
                                   mapper: Callable[[Base], T],
                                   primary_id: str,
                                   production:bool) -> Tuple[bool, Optional[T]]:

        context = get_context()

        where = custom_context_filter(table, context.tenant, production, table.id == primary_id)

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                resource = MysqlQuery(session)
                await resource.delete(table, where)

        async with local_session() as session:
            async with session.begin():
                # Loads regardless of context (production, or test)
                record = await self._custom_load_by_id(table, primary_id=primary_id, production=not production)
                return True, record.map_first_to_object(mapper)


    async def _delete_query(self, table: Type[Base], where):

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                resource = MysqlQuery(session)
                await resource.delete(table, where)

