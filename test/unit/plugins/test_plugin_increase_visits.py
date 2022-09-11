from tracardi.domain.entity import Entity
from tracardi.domain.event import Event, EventSession
from tracardi.domain.event_metadata import EventMetadata, EventTime
from tracardi.domain.session import Session, SessionMetadata

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
    session1 = Session(id="1", metadata=SessionMetadata())
    session1.operation.new = True
    result = run_plugin(IncreaseVisitsAction, init, payload, profile=Profile(id="1"), session=session1, event=event)
    session1.operation.new = False
    result = run_plugin(IncreaseVisitsAction, init, payload, profile=result.profile, session=session1, event=event)
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
    session2 = Session(id="2", metadata=SessionMetadata())
    session2.operation.new = True
    session1 = Session(id="1", metadata=SessionMetadata())
    session1.operation.new = True
    result = run_plugin(IncreaseVisitsAction, init, payload, profile=Profile(id="1"), session=session1, event=event)
    result = run_plugin(IncreaseVisitsAction, init, payload, profile=result.profile, session=session2, event=event)
    assert result.profile.stats.visits == 2



