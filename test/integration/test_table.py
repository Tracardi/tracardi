import pytest
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy.orm import declarative_base

from tracardi.service.storage.mysql.service.table_service import TableService


@pytest.mark.asyncio
async def test_returns_true_if_table_exists():

    Base = declarative_base()

    table = Table('plugin',
                  Base.metadata,
                  Column('id', Integer, primary_key=True),
                  Column('name', String(50))
                  )
    result = await TableService().exists(table)
    assert result is True
