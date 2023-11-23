from tracardi.context import ServerContext, Context, get_context
from tracardi.domain.event_to_profile import EventToProfile, EventToProfileMap
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.ref_value import RefValue
from tracardi.service.storage.mysql.mapping.event_to_profile_mapping import map_to_event_to_profile_table
from tracardi.service.storage.mysql.schema.table import EventToProfileMappingTable
from tracardi.service.storage.mysql.utils.serilizer import to_json


def test_valid_event_to_profile():
    with ServerContext(Context(production=True)):
        prof_map = EventToProfileMap(
                    event=RefValue(ref=True, value="Test Event"),
                    profile=RefValue(ref=True, value="Test Profile"),
                    op=1)
        event_to_profile = EventToProfile(
            id="123",
            name="Test Event",
            event_type=NamedEntity(id="456", name="Test Event Type"),
            tags=["tag1", "tag2"],
            enabled=True,
            config={"key": "value"},
            event_to_profile=[prof_map]
        )

        result = map_to_event_to_profile_table(event_to_profile)

        assert isinstance(result, EventToProfileMappingTable)
        assert result.id == "123"
        assert result.name == "Test Event"
        assert result.description == "No description provided"
        assert result.event_type_id == "456"
        assert result.event_type_name == "Test Event Type"
        assert result.tags == "tag1,tag2"
        assert result.enabled is True
        assert result.config == '{"key": "value"}'
        assert result.event_to_profile == to_json([prof_map])
        assert result.production == get_context().production
