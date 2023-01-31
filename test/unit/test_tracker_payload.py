import pytest

from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.time import Time


def test_should_be_scheduled():
    tp1 = TrackerPayload(
        source=Entity(id="@1"),
        session=None,
        metadata=EventPayloadMetadata(time=Time()),
        profile=Entity(id="2"),
        context={},
        request={},
        properties={},
        events=[EventPayload(type="111222", properties={"node_id": "1"})],
        options={"saveSession": False, 'scheduledFlowId': 'aaabbb'}
    )

    assert tp1.scheduled_flow_id == 'aaabbb'

    tp1 = TrackerPayload(
        source=Entity(id="@1"),
        session=None,
        metadata=EventPayloadMetadata(time=Time()),
        profile=Entity(id="2"),
        context={},
        request={},
        properties={},
        events=[EventPayload(type="111222", properties={"node_id": "1"})],
        options={"saveSession": False, 'scheduledFlowId': True}
    )

    assert tp1.scheduled_flow_id is None

    # incorrect source
    with pytest.raises(ValueError):
        tp1 = TrackerPayload(
            source=Entity(id="1"),
            session=None,
            metadata=EventPayloadMetadata(time=Time()),
            profile=Entity(id="2"),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={"node_id": "1"})],
            options={"saveSession": False, 'scheduledFlowId': "True"}
        )

    with pytest.raises(ValueError):
        tp1 = TrackerPayload(
            source=Entity(id="@1"),
            session=None,
            metadata=EventPayloadMetadata(time=Time()),
            profile=Entity(id="2"),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={"node_id": "1"}), EventPayload(type="111222", properties={})],
            options={"saveSession": False, 'scheduledFlowId': "True"}
        )

    with pytest.raises(ValueError):
        tp1 = TrackerPayload(
            source=Entity(id="@1"),
            session=None,
            metadata=EventPayloadMetadata(time=Time()),
            profile=Entity(id="2"),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
            options={"saveSession": False, 'scheduledFlowId': "True"}
        )

