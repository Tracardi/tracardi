from tracardi.context import ServerContext, Context
from tracardi.domain.entity import Entity
from tracardi.domain.destination import Destination, DestinationConfig
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.storage.mysql.mapping.destination_mapping import map_to_destination_table
from tracardi.service.storage.mysql.utils.serilizer import from_model


def test_maps_destination_to_table():
    with ServerContext(Context(production=True)):

        destination = Destination(
            id="123",
            name="My Destination",
            description="This is a test destination",
            destination=DestinationConfig(package="package", init={"a": 1}),
            enabled=True,
            tags=["tag1", "tag2"],
            mapping={"field1": "value1", "field2": "value2"},
            condition="event@id exists",
            on_profile_change_only=False,
            event_type=NamedEntity(id="event_type_1", name="Event Type 1"),
            source=NamedEntity(id="source_1", name="Source 1"),
            resource=Entity(id="resource_1"),
        )

        result = map_to_destination_table(destination)

        assert result.id == "123"
        assert result.name == "My Destination"
        assert result.production == True
        assert result.description == "This is a test destination"
        assert result.destination == from_model(DestinationConfig(package="package", init={"a": 1}))
        assert result.condition == "event@id exists"
        assert result.mapping == {"field1": "value1", "field2": "value2"}
        assert result.enabled is True
        assert result.on_profile_change_only is False
        assert result.event_type_id == "event_type_1"
        assert result.event_type_name == "Event Type 1"
        assert result.source_id == "source_1"
        assert result.source_name == "Source 1"
        assert result.resource_id == "resource_1"
        assert result.tags == "tag1,tag2"