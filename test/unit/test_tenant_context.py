import pytest

from tracardi.context import ServerContext, Context
from tracardi.service.storage.mysql.schema.table import EventSourceTable
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context, where_with_context, \
    tenant_and_mode_context_filter


def test_table_parameter_type():
    # Initialize
    table = "Not a Base object"

    # Assert
    with pytest.raises(Exception):
        tenant_and_mode_context_filter(table)


def test_tenant_context_filter_positive_path():
    with ServerContext(Context(production=False)):
        # Initialize
        where = tenant_and_mode_context_filter(
            EventSourceTable
        )

        assert str(where) == 'event_source.tenant = :tenant_1 AND event_source.production = false'


def test_where_tenant_context_positive_path():
    with ServerContext(Context(production=True)):
        # Initialize
        where = where_tenant_and_mode_context(
            EventSourceTable,
            EventSourceTable.id == '1'
        )

        assert str(where()) == 'event_source.tenant = :tenant_1 AND event_source.production = true AND event_source.id = :id_1'


def test_where_with_context_positive_path():
    with ServerContext(Context(production=True)):
        # Initialize
        where = where_with_context(
            EventSourceTable,
            True,
            EventSourceTable.id == '1'
        )

        assert str(where()) == 'event_source.tenant = :tenant_1 AND event_source.production = true AND event_source.id = :id_1'


        where = where_with_context(
            EventSourceTable,
            False,
            EventSourceTable.id == '1'
        )

        assert str(where()) == 'event_source.tenant = :tenant_1 AND event_source.id = :id_1'