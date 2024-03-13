from typing import Type, Callable, TypeVar

from tracardi.context import get_context
from sqlalchemy import and_
from sqlalchemy.sql import func

from tracardi.service.storage.mysql.schema.table import Base

T = TypeVar('T')


def tenant_only_context_filter(table: Type[Base]):
    context = get_context()
    return table.tenant == context.tenant


def custom_context_filter(table: Type[Base], tenant: str, production: bool, *clauses):
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


def _where_only_tenant_context(table: Type[Base], *clauses) -> Callable:
    def _wrapper():
        return and_(tenant_only_context_filter(table), *clauses)

    return _wrapper


def sql_functions():
    return func


def where_with_context(table: Type[Base], server_context: bool, *clauses) -> Callable:
    return where_tenant_and_mode_context(
        table,
        *clauses
    ) if server_context else _where_only_tenant_context(
        table,
        *clauses
    )
