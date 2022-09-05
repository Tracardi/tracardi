from tracardi.domain.entity import Entity
from tracardi.domain.event import Event, EventSession
from tracardi.domain.event_metadata import EventMetadata, EventTime
from tracardi.process_engine.action.v1.increase_views_action import IncreaseViewsAction
from tracardi.domain.profile import Profile
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_plugin_increase_views():
    init = {}

    payload = {}
    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )
    result = run_plugin(IncreaseViewsAction, init, payload, profile=Profile(id="1"), event=event)
    result = run_plugin(IncreaseViewsAction, init, payload, profile=result.profile, event=event)
    assert result.profile.stats.views == 2



