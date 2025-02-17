from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.event_session import EventSession
from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.flat_session import FlatSession
from tracardi.domain.time import EventTime

from tracardi.process_engine.action.v1.increase_visits_action import IncreaseVisitsAction
from tracardi.domain.profile import Profile
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_plugin_increase_visits_1():
    init = {}
    payload = {}
    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )
    flat_session1 = FlatSession.new(id="1")
    flat_session1.set_new(True)
    result = run_plugin(IncreaseVisitsAction, init, payload, profile=Profile(id="1"), session=flat_session1, event=event)
    flat_session1.set_new(False)
    result = run_plugin(IncreaseVisitsAction, init, payload, profile=result.profile, session=flat_session1, event=event)
    assert result.profile.stats.visits == 1


def test_plugin_increase_visits_2():
    init = {}
    payload = {}
    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )
    flat_session2 = FlatSession.new(id="2")
    flat_session2.set_new(True)
    flat_session1 = FlatSession.new(id="1")
    flat_session1.set_new(True)
    result = run_plugin(IncreaseVisitsAction, init, payload, profile=Profile(id="1"), session=flat_session1, event=event)
    result = run_plugin(IncreaseVisitsAction, init, payload, profile=result.profile, session=flat_session2, event=event)
    assert result.profile.stats.visits == 2



