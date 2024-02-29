from tracardi.context import ServerContext, Context
from tracardi.domain.identification_point import IdentificationPoint, IdentificationField
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.ref_value import RefValue
from tracardi.service.storage.mysql.mapping.identification_point_mapping import map_to_identification_point_table, \
    map_to_identification_point
from tracardi.service.storage.mysql.schema.table import IdentificationPointTable
from tracardi.service.storage.mysql.utils.serilizer import to_json, from_model


def test_returns_instance_of_identification_point_table():
    with ServerContext(Context(production=True)):
        identification_point = IdentificationPoint(
            id="1",
            name="Point 1",
            description="This is point 1",
            source=NamedEntity(id="source1", name="Source 1"),
            event_type=NamedEntity(id="event1", name="Event 1"),
            fields=[
                IdentificationField(
                    profile_trait=RefValue(ref=True, value="Test Event"),
                    event_property=RefValue(ref=True, value="Test Profile"),
                )
            ],
            settings={"setting1": "value1", "setting2": "value2"}
        )

        result = map_to_identification_point_table(identification_point)

        assert isinstance(result, IdentificationPointTable)

        assert result.id == identification_point.id
        assert result.name == identification_point.name
        assert result.description == identification_point.description
        assert result.source_id == identification_point.source.id
        assert result.source_name == identification_point.source.name
        assert result.event_type_id == identification_point.event_type.id
        assert result.event_type_name == identification_point.event_type.name
        assert result.fields == from_model(identification_point.fields)
        assert result.enabled is False
        assert result.settings == identification_point.settings

def test_correctly_map_identification_point_table_to_identification_point():
    fields = [
        IdentificationField(
            profile_trait=RefValue(ref=True, value="Test Event"),
            event_property=RefValue(ref=True, value="Test Profile"),
        )
    ]

    identification_point_table = IdentificationPointTable(
        id="123",
        name="Test",
        description="Test description",
        source_id="456",
        source_name="Source",
        event_type_id="789",
        event_type_name="Event",
        fields=from_model(fields),
        settings={}
    )

    identification_point = map_to_identification_point(identification_point_table)

    assert identification_point.id == "123"
    assert identification_point.name == "Test"
    assert identification_point.description == "Test description"
    assert identification_point.source.id == "456"
    assert identification_point.source.name == "Source"
    assert identification_point.event_type.id == "789"
    assert identification_point.event_type.name == "Event"
    assert len(identification_point.fields) == 1
    assert identification_point.fields == fields
    assert identification_point.enabled is False