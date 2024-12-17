from datetime import datetime
from uuid import uuid4

from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.flat_event import EventDict
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.event_source import EventSource
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.time import Time
from tracardi.service.tracking.compute.event.event_construction import event_payload_to_event


def test_event_payload_to_event():
    # Prepare data for the test
    event_payload = EventPayload(
        id=str(uuid4()),
        type="test-event",
        properties={"key": "value"},
        context={"page": {"title": "Test Page", "url": "https://test.com", "referer": {"host": "test.com"}}},
        tags=["test", "event"]
    )

    metadata = EventPayloadMetadata(
        time=Time(),
        ip="127.0.0.1",
        status="collected"
    )

    source = EventSource(
        id="1",
        name="test",
        type=["test"],
        bridge=NamedEntity(id="test-bridge", name="bridge"),
        timestamp=datetime.utcnow()
    )

    session = Session(
        id=str(uuid4()),
        metadata=SessionMetadata(),
        context={"time_zone": "UTC"}
    )

    # Call the function under test
    event, is_valid = event_payload_to_event({"test": 1}, event_payload, metadata, source, session, "1", profile_less=False)

    # Validate the result
    assert isinstance(event, EventDict)
    assert event['type'] == "test-event"
    assert event['name'] == "Test Event"
    assert event['properties'] == {"key": "value"}
    assert event['metadata']['status'] == "collected"
    assert event['session']['id'] == session.id
    assert event['profile']['id'] == "1"
    assert event['tags']['values'] == ("test", "event")
    assert event['hit']['name'] == "Test Page"
    assert event['hit']['url'] == "https://test.com"
    assert event['hit']['referer'] == "test.com"
    assert event['request'] == {"test": 1}


def test_event_payload_to_event_no_session():
    # Prepare data for the test without session
    event_payload = EventPayload(
        id=str(uuid4()),
        type="test-event",
        properties={"key": "value"},
        tags=["test", "event"]
    )

    metadata = EventPayloadMetadata(
        time=Time(),
        ip="127.0.0.1",
        status="collected"
    )

    source = EventSource(
        id="1",
        name="test",
        type=["test"],
        bridge=NamedEntity(id="test-bridge", name="bridge"),
        timestamp=datetime.utcnow()
    )

    # Call the function under test
    event, is_valid = event_payload_to_event({}, event_payload, metadata, source, None, "1", profile_less=False)

    # Validate the result
    assert isinstance(event, EventDict)
    assert event['type'] == "test-event"
    assert event['name'] == "Test Event"
    assert event['properties'] == {"key": "value"}
    assert event['metadata']['status'] == "collected"
    assert event['session'] is None
    assert event['tags']['values'] == ("test", "event")
