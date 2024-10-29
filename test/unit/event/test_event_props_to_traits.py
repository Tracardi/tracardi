import pytest
from dotty_dict import Dotty

from com_tracardi.service.event_mapper import map_event_props_to_traits, map_events_tags_and_journey
from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.domain.flat_event import FlatEvent


@pytest.fixture
def event_data():
    return FlatEvent({
        "id": "event-123",
        "properties": {
            "prop1": "value1",
            "prop2": "value2"
        },
        "traits": {},
        "tags": {
            "values": ["existing-tag"]
        },
        "journey": {
            "state": "initial"
        }
    })


@pytest.fixture
def event_mapping_enabled():
    return EventTypeMetadata(
        id='1',
        name="test",
        event_type="test",
        enabled=True,
        index_schema={
            "prop1": "trait1",
            "prop2": "trait2"
        },
        tags=["new-tag"],
        journey="in-progress"
    )


@pytest.fixture
def event_mapping_disabled():
    return EventTypeMetadata(
        id='1',
        name="test",
        event_type="test",
        enabled=False,
        index_schema={
            "prop1": "trait1"
        },
        tags=[],
        journey=None
    )


def test_map_event_props_to_traits_enabled_mapping(event_data, event_mapping_enabled):
    # Call the function with event mapping enabled
    updated_event = map_event_props_to_traits(event_data, event_mapping_enabled)
    print(updated_event)
    # Check that properties were moved to traits
    assert "trait1" in updated_event["traits"]
    assert updated_event["traits"]["trait1"] == "value1"
    assert "trait2" in updated_event["traits"]
    assert updated_event["traits"]["trait2"] == "value2"

    # Check that the properties are removed from event properties
    assert "prop1" not in updated_event["properties"]
    assert "prop2" not in updated_event["properties"]


def test_map_event_props_to_traits_disabled_mapping(event_data, event_mapping_disabled):
    # Call the function with event mapping disabled
    updated_event = map_event_props_to_traits(event_data, event_mapping_disabled)

    # Check that traits are not modified because mapping is disabled
    assert "traits" in updated_event
    assert updated_event["traits"] == {}

    # Check that properties remain unchanged
    assert "prop1" in updated_event["properties"]
    assert updated_event["properties"]["prop1"] == "value1"
    assert "prop2" in updated_event["properties"]
    assert updated_event["properties"]["prop2"] == "value2"


def test_map_event_props_to_traits_no_mapping(event_data):
    # Call the function with no mapping provided
    updated_event = map_event_props_to_traits(event_data, None)

    # Check that traits are not modified
    assert "traits" in updated_event
    assert updated_event["traits"] == {}

    # Check that properties remain unchanged
    assert "prop1" in updated_event["properties"]
    assert updated_event["properties"]["prop1"] == "value1"
    assert "prop2" in updated_event["properties"]
    assert updated_event["properties"]["prop2"] == "value2"


def test_map_events_tags_and_journey(event_data, event_mapping_enabled):
    # Call the function with event mapping enabled
    updated_event = map_events_tags_and_journey(event_data, event_mapping_enabled)

    assert isinstance(updated_event, Dotty)
    # Check that tags are updated correctly
    assert "existing-tag" in updated_event["tags"]["values"]
    assert "new-tag" in updated_event["tags"]["values"]
    assert len(updated_event["tags"]["values"]) == 2

    # Check that journey state is updated
    assert updated_event["journey"]["state"] == "in-progress"


def test_map_events_tags_and_journey_no_mapping(event_data):
    # Call the function with no mapping provided
    updated_event = map_events_tags_and_journey(event_data, None)

    # Check that tags and journey remain unchanged
    assert updated_event["tags"]["values"] == ["existing-tag"]
    assert updated_event["journey"]["state"] == "initial"


def test_map_events_tags_and_journey_disabled_mapping(event_data, event_mapping_disabled):
    # Call the function with event mapping disabled
    updated_event = map_events_tags_and_journey(event_data, event_mapping_disabled)

    # Check that tags and journey remain unchanged
    assert updated_event["tags"]["values"] == ["existing-tag"]
    assert updated_event["journey"]["state"] == "initial"
