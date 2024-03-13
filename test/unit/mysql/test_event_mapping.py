from tracardi.context import ServerContext, Context
from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.service.storage.mysql.mapping.event_to_event_mapping import map_to_event_mapping_table, \
    map_to_event_mapping
from tracardi.service.storage.mysql.schema.table import EventMappingTable


def test_same_values():
    with ServerContext(Context(production=True)):
        event_type_metadata = EventTypeMetadata(
            id="123",
            name="Test Event",
            description="This is a test event",
            event_type="test-event",
            tags=["tag1", "tag2"],
            journey="test_journey",
            enabled=True,
            index_schema={"field1": "text", "field2": "keyword"}
        )

        expected_mapping_table = EventMappingTable(
            id="test-event",
            name="Test Event",
            description="This is a test event",
            event_type="test-event",
            tags="tag1,tag2",
            journey="test_journey",
            enabled=True,
            index_schema={"field1": "text", "field2": "keyword"}
        )

        mapping_table = map_to_event_mapping_table(event_type_metadata)
        assert mapping_table.id == expected_mapping_table.id
        assert mapping_table.name == expected_mapping_table.name
        assert mapping_table.description == expected_mapping_table.description
        assert mapping_table.event_type == expected_mapping_table.event_type
        assert ",".join(event_type_metadata.tags) == expected_mapping_table.tags
        assert mapping_table.enabled == expected_mapping_table.enabled
        assert mapping_table.index_schema == expected_mapping_table.index_schema


def test_valid_event_mapping_table():
    event_mapping_table = EventMappingTable(
        id="1",
        name="Test Event",
        description="Test event description",
        event_type="test.event",
        tags="tag1,tag2",
        journey="test_journey",
        enabled=True,
        index_schema={"field": "value"}
    )
    expected_result = EventTypeMetadata(
        id="1",
        name="Test Event",
        description="Test event description",
        event_type="test.event",
        tags=["tag1", "tag2"],
        journey="test_journey",
        enabled=True,
        index_schema={"field": "value"}
    )
    assert map_to_event_mapping(event_mapping_table) == expected_result
