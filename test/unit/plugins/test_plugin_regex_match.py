from tracardi.service.plugin.service.plugin_runner import run_plugin
from tracardi.process_engine.action.v1.strings.regex_match.plugin import RegexMatchAction
from tracardi.domain.profile import Profile
from tracardi.domain.event import Event, EventSession
from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventMetadata, EventTime


def test_should_work():
    init = {
        "pattern": "[a-z]{5}",
        "text": "payload@text",
        "group_prefix": "Group"
    }
    payload = {
        "text": "Lorem ipsum dolor sit amet"
    }

    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )

    result = run_plugin(RegexMatchAction, init, payload, profile=Profile(id="1"), event=event)

    assert result.output.value == {"Group-0": "ipsum", "Group-1": "dolor"}
