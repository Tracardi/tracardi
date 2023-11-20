from typing import Optional, Type

from sqlalchemy.dialects.mysql import insert
from tracardi.service.storage.mysql.engine import AsyncMySqlEngine
from sqlalchemy.future import select
from sqlalchemy import and_, delete, inspect, update, Column

from tracardi.service.storage.mysql.schema.table import Base
from tracardi.service.storage.mysql.schema.table import local_context_filter, local_context_entity
from tracardi.service.storage.mysql.utils.select_result import SelectResult


class TableService:

    def __init__(self):
        self.client = AsyncMySqlEngine()
        self.engine = self.client.get_engine_for_database()

    async def _load_all(self, table: Type[Base]) -> SelectResult:
        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                result = await session.execute(select(table).where(local_context_filter(table)))
                # Fetch all results
                bridges = result.scalars().all()
                return SelectResult(bridges)

    async def _load_by_id(self, table: Type[Base], primary_id: str) -> SelectResult:
        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                result = await session.execute(select(table).where(local_context_entity(table, primary_id)))
                # Fetch all results
                return SelectResult(result.scalars().one_or_none())


    async def _field_filter(self, table: Type[Base], field: Column, value) -> SelectResult:
        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            # Start a new transaction
            async with session.begin():
                # Use SQLAlchemy core to perform an asynchronous query
                result = await session.execute(select(table).where(
                    and_(
                        local_context_filter(table),
                        field == value
                    )
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

    async def _update(self, table: Type[Base], primary_id: str, new_data: dict) -> Optional[str]:
        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                stmt = (
                    update(table)
                    .where(local_context_entity(table, primary_id))
                    .values(**new_data)
                )
                await session.execute(stmt)
                await session.commit()
                return primary_id

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

    async def _insert_if_none(self, table: Type[Base], data) -> Optional[str]:

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():

                existing_row = (await session.execute(
                    select(table).where(
                        and_(local_context_entity(table, data.id))
                    ))).scalar()

                if existing_row is None:

                    # Add the new object to the session
                    session.add(data)

                    # The actual commit happens here
                    await session.commit()

                    # Return the id of the new record
                    return data.id

                return None

    async def _delete(self, table: Type[Base], primary_id: str) -> str:

        local_session = self.client.get_session(self.engine)
        async with local_session() as session:
            async with session.begin():
                await session.execute(
                    delete(table).where(
                        and_(local_context_filter(table), table.id == primary_id)
                ))

                return primary_id
