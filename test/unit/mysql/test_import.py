from tracardi.context import ServerContext, Context
from tracardi.domain.import_config import ImportConfig
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.mapping.import_mapping import map_to_import_config_table, map_to_import_config
from tracardi.service.storage.mysql.schema.table import ImportTable


def test_map_import_table():
    with ServerContext(Context(production=True)):
        # Arrange
        import_config = ImportConfig(
            id="123",
            name="Test Import",
            description="This is a test import",
            module="test_module",
            config={"key": "value"},
            enabled=True,
            api_url="http://test-api.com",
            event_source=NamedEntity(id="456", name="Test Event Source"),
            event_type="Test Event Type"
        )

        # Act
        result = map_to_import_config_table(import_config)

        # Assert
        assert isinstance(result, ImportTable)


def test_map_import_table_to_import_config():
        import_table = ImportTable(
            id="123",
            name="Test Import",
            description="This is a test import",
            module="test_module",
            config={},
            enabled=True,
            transitional=False,
            api_url="http://test.com",
            event_source_id="456",
            event_source_name="Test Event Source",
            event_type="Test Event Type",
            tenant="test_tenant",
            production=True
        )

        expected_import_config = ImportConfig(
            id="123",
            name="Test Import",
            description="This is a test import",
            module="test_module",
            config={},
            enabled=True,
            api_url="http://test.com",
            event_source=NamedEntity(id="456", name="Test Event Source"),
            event_type="Test Event Type"
        )

        assert map_to_import_config(import_table) == expected_import_config