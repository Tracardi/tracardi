from tracardi.context import Context, ServerContext
from tracardi.domain.event_reshaping_schema import EventReshapingSchema, ReshapeSchema, EventReshapeDefinition
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.mapping.event_reshaping_mapping import map_to_event_reshaping_table, \
    map_to_event_reshaping
from tracardi.service.storage.mysql.schema.table import EventReshapingTable
from tracardi.service.storage.mysql.utils.serilizer import from_model


def test_map_to_event_reshaping_table_mapping():

    with ServerContext(Context(production=True)):
        # Arrange
        event_reshaping = EventReshapingSchema(
            id="123",
            name="Test Event Reshaping",
            event_type="test_event",
            event_source=NamedEntity(id="456", name="Test Event Source"),
            reshaping=ReshapeSchema(reshape_schema=EventReshapeDefinition()),
            tags=["tag1", "tag2"],
            description="Test description"
        )

        result = map_to_event_reshaping_table(event_reshaping)

        # Assert
        assert isinstance(result, EventReshapingTable)
        assert result.id == "123"
        assert result.name == "Test Event Reshaping"
        assert result.event_type == "test_event"
        assert result.event_source_id == "456"
        assert result.event_source_name == "Test Event Source"
        assert result.reshaping == from_model(ReshapeSchema(reshape_schema=EventReshapeDefinition()))
        assert result.enabled is False
        assert result.tags == "tag1,tag2"
        assert result.description == "Test description"


def test_correctly_map_fields():
    reshaping = ReshapeSchema(reshape_schema=EventReshapeDefinition())
    event_reshaping_table = EventReshapingTable(
        id="123",
        name="Test Reshaping",
        description="Test description",
        reshaping=from_model(reshaping),
        tags="tag1,tag2",
        event_type="test_event",
        event_source_id="456",
        event_source_name="Test Source",
        enabled=True
    )

    expected_event_reshaping = EventReshapingSchema(
        id="123",
        name="Test Reshaping",
        description="Test description",
        reshaping=reshaping,
        tags=["tag1", "tag2"],
        event_type="test_event",
        event_source=NamedEntity(id="456", name="Test Source"),
        enabled=True
    )

    actual_event_reshaping = map_to_event_reshaping(event_reshaping_table)

    assert actual_event_reshaping == expected_event_reshaping