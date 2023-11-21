import pytest

from tracardi.context import ServerContext, Context
from tracardi.service.storage.mysql.schema.table import tenant_context_filter, Base, BridgeTable, PluginTable
from tracardi.service.storage.mysql.service.table_service import where_tenant_context, where_with_context


def test_table_parameter_type():
    # Initialize
    table = "Not a Base object"

    # Assert
    with pytest.raises(Exception):
        tenant_context_filter(table)


def test_tenant_context_filter_positive_path():
    with ServerContext(Context(production=False)):
        # Initialize
        where = tenant_context_filter(
            PluginTable
        )

        assert str(where) == 'plugin.tenant = :tenant_1 AND plugin.production = false'


def test_where_tenant_context_positive_path():
    with ServerContext(Context(production=True)):
        # Initialize
        where = where_tenant_context(
            PluginTable,
            PluginTable.id == '1'
        )

        assert str(where) == 'plugin.tenant = :tenant_1 AND plugin.production = true AND plugin.id = :id_1'


def test_where_with_context_positive_path():
    with ServerContext(Context(production=True)):
        # Initialize
        where = where_with_context(
            PluginTable,
            True,
            PluginTable.id == '1'
        )

        assert str(where) == 'plugin.tenant = :tenant_1 AND plugin.production = true AND plugin.id = :id_1'


        where = where_with_context(
            PluginTable,
            False,
            PluginTable.id == '1'
        )

        assert str(where) == 'plugin.tenant = :tenant_1 AND plugin.id = :id_1'