import pytest

from tracardi.domain.entity import Entity, PrimaryEntity
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.time import Time


def test_should_be_scheduled():
    tp1 = TrackerPayload(
        source=Entity(id="@1"),
        session=None,
        metadata=EventPayloadMetadata(time=Time()),
        profile=PrimaryEntity(id="2"),
        context={},
        request={},
        properties={},
        events=[EventPayload(type="111222", properties={})],
        options={"saveSession": False, 'scheduledFlowId': 'aaabbb', 'scheduledNodeId': "111"}
    )

    assert tp1.scheduled_event_config.flow_id == 'aaabbb'
    assert tp1.scheduled_event_config.node_id == '111'

    tp1 = TrackerPayload(
        source=Entity(id="@1"),
        session=None,
        metadata=EventPayloadMetadata(time=Time()),
        profile=PrimaryEntity(id="2"),
        context={},
        request={},
        properties={},
        events=[EventPayload(type="111222", properties={})],
        options={"saveSession": False, 'scheduledFlowId': True, 'scheduledNodeId': "1"}
    )

    assert tp1.scheduled_event_config.flow_id is None
    assert tp1.scheduled_event_config.is_scheduled() is False

    # incorrect source
    with pytest.raises(ValueError):
        tp1 = TrackerPayload(
            source=Entity(id="1"),
            session=None,
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id="2"),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={})],
            options={"saveSession": False, 'scheduledFlowId': "True", 'scheduledNodeId': "1"}
        )

    with pytest.raises(ValueError):
        tp1 = TrackerPayload(
            source=Entity(id="@1"),
            session=None,
            metadata=EventPayloadMetadata(time=Time()),
            profile=PrimaryEntity(id="2"),
            context={},
            request={},
            properties={},
            events=[EventPayload(type="111222", properties={}), EventPayload(type="111222", properties={})],
            options={"saveSession": False, 'scheduledFlowId': "True", 'scheduledNodeId': "1"}
        )

    tp1 = TrackerPayload(
        source=Entity(id="@1"),
        session=None,
        metadata=EventPayloadMetadata(time=Time()),
        profile=PrimaryEntity(id="2"),
        context={},
        request={},
        properties={},
        events=[EventPayload(type="111222", properties={})],
        options={"saveSession": False, 'scheduledFlowId': "True"}
    )

    assert tp1.scheduled_event_config.is_scheduled() is False
