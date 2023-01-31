from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.time import Time


def test_should_be_scheduled():
    tp1 = TrackerPayload(
        source=Entity(id="1"),
        session=None,
        metadata=EventPayloadMetadata(time=Time()),
        profile=Entity(id="2"),
        context={},
        request={},
        properties={},
        events=[EventPayload(type="111222", properties={}, schedule="aaabbb")],
        options={"saveSession": False}
    )

    for ep in tp1.events:
        event = ep.to_event(
            EventPayloadMetadata(time=Time()),
            source=Entity(id="1"),
            session=None,
            profile=None,
            has_profile=False
        )
        assert event.scheduled_flow_id == "aaabbb"
