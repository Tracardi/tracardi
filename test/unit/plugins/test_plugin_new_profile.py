from tracardi.domain.entity import Entity
from tracardi.domain.event import Event, EventSession
from tracardi.domain.event_metadata import EventMetadata, EventTime
from tracardi.process_engine.action.v1.new_profile_action import NewProfileAction
from tracardi.domain.profile import Profile
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_plugin_new_profile_true():
    init = {}
    payload = {}
    profile = Profile(id="1")
    profile.operation.new = True
    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )
    result = run_plugin(NewProfileAction, init, payload, profile=profile, event=event)
    assert result.output.value == payload
    assert result.output.port == 'true'


def test_plugin_new_profile_false():
    init = {}
    payload = {}
    profile = Profile(id="1")
    profile.operation.new = False
    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )

    result = run_plugin(NewProfileAction, init, payload, profile=profile, event=event)
    assert result.output.value == payload
    assert result.output.port == 'false'
