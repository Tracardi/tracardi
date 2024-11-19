import datetime

from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.event_source import EventSource
from tracardi.domain.named_entity import NamedEntity

from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.time import Time
from tracardi.service.tracking.compute.event.event_construction import event_payload_to_event


def test_event_payload_time_fallback():
    ep = EventPayload(
        type="text",
        tags=["tag1", "tag2", "tag3"],
        time=Time(
            create="2001-01-01 00:00:00"   # Time for event (local)
        )
    )

    tracker_payload_metadata = EventPayloadMetadata(
        time=Time(
            insert="2002-01-01 00:00:00",  # Times from whole tracker payload
            create="2004-01-01 00:00:00"
        )
    )
    event, _ = event_payload_to_event(
        {},
        ep,
        tracker_payload_metadata,
        source=EventSource(id="1", name="test", type=["rest"], bridge=NamedEntity(id="1", name="rest")),
        session=Session(id="1", metadata=SessionMetadata()),
        profile_id="1",
        profile_less=False
    )

    assert event['metadata']['time']['insert'] != "2002-01-01T00:00:00Z"  # Must be now - can not be overridden
    assert event['metadata']['time']['create'] == "2001-01-01T00:00:00Z"


def test_event_payload_should_have_tags():
    ep = EventPayload(type="text", tags=["tag1", "tag2", "tag3"])

    epm = EventPayloadMetadata(
        time=Time(
            insert=datetime.datetime(2002, 1, 1, 0, 0),
            create=datetime.datetime(2002, 1, 1, 0, 0)
        )
    )
    event, _ = event_payload_to_event({},
                                      ep,
                                      epm,
                                      source=EventSource(id="1", name="test", type=["rest"],
                                                         bridge=NamedEntity(id="1", name="rest")),
                                      session=Session(id="1", metadata=SessionMetadata()),
                                      profile_id="1",
                                      profile_less=False
                                      )

    assert event['tags']['values'] == ('tag1', 'tag2', 'tag3')
    assert event['tags']['count'] == 3
