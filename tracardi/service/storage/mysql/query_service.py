from tracardi.context import get_context
from tracardi.service.storage.mysql.schema.table import Base
from tracardi.service.storage.mysql.utils.select_result import SelectResult

from typing import Type, Any, Callable, Optional, Tuple

from sqlalchemy import Column, Select, update, delete, ChunkedIteratorResult, and_
from sqlalchemy.future import select


def context_filter(table: Type[Base], tenant: str, production: bool, *clauses):
    def _wrapper():
        return and_(table.tenant == tenant, table.production == production, *clauses)

    return _wrapper

class MySqlQueryResult:

    """
    Standardizes the output form MysqlQuery
    """

    def __init__(self, data):
        self.data = data

    def all(self):
        if isinstance(self.data, ChunkedIteratorResult):
            return self.data.scalars().all()
        else:
            return self.data

    def one_or_none(self):
        if isinstance(self.data, ChunkedIteratorResult):
            return self.data.scalars().one_or_none()
        else:
            return self.data[0] if self.data else None


    def one(self):
        if isinstance(self.data, ChunkedIteratorResult):
            return self.data.scalars().one()
        else:
            return self.data[0]

    def empty(self) -> bool:
        if isinstance(self.data, ChunkedIteratorResult):
            return self.data.first() is None
        else:
            return not bool(self.data)

class MysqlQuery:

    def __init__(self, session):
        self.session = session

    @staticmethod
    def _select_clause(table: Type[Base],
                       columns=None,
                       where: Optional[Callable] = None,
                       order_by: Column = None,
                       limit: int = None,
                       offset: int = None,
                       distinct: bool = False) -> Select[Any]:

        if columns is not None:
            _select = select(*columns)
        else:
            _select = select(table)

        if distinct:
            _select = _select.distinct()

        if where is not None:
            _select = _select.where(where())

        if order_by is not None:
            _select = _select.order_by(order_by)

        if limit:
            _select = _select.limit(limit)

            if offset:
                _select = _select.offset(offset)

        return _select

    async def update(self, table: Type[Base], new_data, where: Optional[Callable] = None):
        stmt = (
            update(table)
            .where(where())
            .values(**new_data)
        )
        return await self.session.execute(stmt)

    async def delete(self, table: Type[Base], where: Optional[Callable] = None):
        return await self.session.execute(
            delete(table).where(where())
        )

    async def select(self, table: Type[Base],
                     columns=None,
                     where: Optional[Callable] = None,
                     order_by: Column = None,
                     limit: int = None,
                     offset: int = None,
                     distinct: bool = False) -> MySqlQueryResult:
        context = get_context()

        query = self._select_clause(table,
                                    columns,
                                    where,
                                    order_by,
                                    limit,
                                    offset,
                                    distinct)

        return MySqlQueryResult(await self.session.execute(query))

    def insert(self, data):
        return self.session.add(data)

class MysqlQueryInDeploymentMode(MysqlQuery):

    async def delete_by_id(self, table: Type[Base], primary_id) -> Tuple[bool, SelectResult]:
        context = get_context()

        where = context_filter(table, context.tenant, context.production, table.id == primary_id)
        await self.session.execute(
            delete(table).where(where())
        )

        return True, SelectResult(None)
