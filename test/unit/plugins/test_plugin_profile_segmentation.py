from tracardi.service.plugin.service.plugin_runner import run_plugin
from tracardi.process_engine.action.v1.segmentation.profile_segmentation.plugin import ProfileSegmentAction
from tracardi.domain.profile import Profile
from tracardi.domain.event import Event, EventSession
from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventMetadata, EventTime


def test_should_add_to_segment():
    init = {
        "condition": "payload@value == 1",
        "true_segment": "True-Segment",
        "true_action": "add",
        "false_segment": "False-Segment",
        "false_action": "remove"
    }
    payload = {
        "value": 1
    }

    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )

    result = run_plugin(ProfileSegmentAction, init, payload, profile=Profile(id="1"), event=event)

    assert result.output.port == "true"
    assert result.profile.segments == ["True-Segment"]


def test_should_remove_from_segment():
    init = {
        "condition": "payload@value == 2",
        "true_segment": "True-Segment",
        "true_action": "add",
        "false_segment": "False-Segment",
        "false_action": "remove"
    }
    payload = {
        "value": 1
    }

    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )

    result = run_plugin(ProfileSegmentAction, init, payload, profile=Profile(id="1", segments=["False-Segment"]),
                        event=event)

    assert result.output.port == "false"
    assert result.profile.segments == []

    
def test_should_do_nothing():
    init = {
        "condition": "payload@value == 2",
        "true_segment": "True-Segment",
        "true_action": "add",
        "false_segment": "False-Segment",
        "false_action": "none"
    }
    payload = {
        "value": 1
    }

    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )

    result = run_plugin(ProfileSegmentAction, init, payload, profile=Profile(id="1", segments=["Some-Segment"]),
                        event=event)

    assert result.output.port == "false"
    assert result.profile.segments == ["Some-Segment"]
