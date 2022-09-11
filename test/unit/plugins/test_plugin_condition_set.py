from tracardi.service.plugin.service.plugin_runner import run_plugin
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event, EventSession
from tracardi.domain.event_metadata import EventMetadata, EventTime
from tracardi.process_engine.action.v1.traits.condition_set.plugin import ConditionSetPlugin
from tracardi.domain.profile import Profile


def test_plugin_condition_set():
    init = {'conditions': {
        "isProfileID": "profile@id == \"1\"",
        "is-event-pageview": "event@type == \"page-view\""
    }}
    payload = {}
    profile = Profile(id='1')
    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )
    result = run_plugin(ConditionSetPlugin, init, payload, profile=profile, event=event)

    assert result.output.value == {'isProfileID': True, 'is-event-pageview': False}
    assert result.output.port == "result"
