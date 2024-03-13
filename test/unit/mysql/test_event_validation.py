from tracardi.context import ServerContext, Context
from tracardi.domain.event_validator import EventValidator, ValidationSchema
from tracardi.service.storage.mysql.mapping.event_validation_mapping import map_to_event_validation_table, \
    map_to_event_validation
from tracardi.service.storage.mysql.schema.table import EventValidationTable


def test_valid_event_validator():
    with ServerContext(Context(production=True)):
        v = ValidationSchema(json_schema={}, condition="event@id exists")
        event_validator = EventValidator(
            id="123",
            name="Test Validator",
            event_type="test.event",
            validation=v
        )
        result = map_to_event_validation_table(event_validator)

        assert isinstance(result, EventValidationTable)
        assert result.id == "123"
        assert result.name == "Test Validator"
        assert result.event_type == "test.event"
        assert result.validation == v.model_dump(mode='json')
        assert result.tags == ""
        assert result.enabled is False

def test_correctly_map_fields():
        table = EventValidationTable(
            id="123",
            name="Test",
            description="Test description",
            validation={"json_schema": {}},
            tags="tag1,tag2",
            event_type="event_type",
            enabled=False
        )

        expected_validator = EventValidator(
            id="123",
            name="Test",
            description="Test description",
            validation=ValidationSchema(json_schema={}),
            tags=["tag1", "tag2"],
            event_type="event_type",
            enabled=False
        )

        result = map_to_event_validation(table)

        assert result == expected_validator