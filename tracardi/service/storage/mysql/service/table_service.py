from typing import Optional, Type

from sqlalchemy.dialects.mysql import insert
from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
from sqlalchemy.future import select
from sqlalchemy import and_, delete, inspect, update, Column

from tracardi.service.storage.mysql.schema.table import Base, tenant_only_context_filter
from tracardi.service.storage.mysql.schema.table import tenant_context_filter
from tracardi.service.storage.mysql.utils.select_result import SelectResult

def where_tenant_context(table, *clauses):
    return and_(tenant_context_filter(table), *clauses)


def where_only_tenant_context(table, *clauses):
    return and_(tenant_only_context_filter(table), *clauses)


def where_with_context(table: Type[Base], server_context:bool, *clauses):
    return where_tenant_context(
        table,
        *clauses
    ) if server_context else where_only_tenant_context(
        table,
        *clauses
    )


class TableService:

    def __init__(self):
        self.client = AsyncMySqlEngine()
        self.engine = self.client.get_engine_for_database()

    async def _load_all(self, table: Type[Base], server_context:bool=True) -> SelectResult:
        local_session = self.client.get_session(self.engine)

        where = where_with_context(table, server_context)
            
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                result = await session.execute(select(table).where(where))
                # Fetch all results
                bridges = result.scalars().all()
                return SelectResult(bridges)

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

    async def _where(self, table: Type[Base], where) -> SelectResult:
        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                result = await session.execute(select(table).where(
                    where
                ))
                # Fetch all results
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

    async def _update_by_query(self, table: Type[Base], where, new_data: dict):
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
