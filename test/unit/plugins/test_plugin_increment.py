from tracardi.domain.entity import Entity
from tracardi.domain.event import Event, EventSession
from tracardi.domain.event_metadata import EventMetadata, EventTime
from tracardi.process_engine.action.v1.increment_action import IncrementAction

from tracardi.domain.profile import Profile
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_plugin_increment():
    init = {
        "field": "profile@stats.counters.x",
        "increment": 1
    }

    payload = {}
    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )
    result = run_plugin(IncrementAction, init, payload, profile=Profile(id="1"), event=event)
    assert result.profile.stats.counters['x'] == 1


def test_plugin_increment_2():
    init = {
        "field": "profile@stats.counters.x",
        "increment": 2
    }

    payload = {}
    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )
    result = run_plugin(IncrementAction, init, payload, profile=Profile(id="1"), event=event)
    assert result.profile.stats.counters['x'] == 2
