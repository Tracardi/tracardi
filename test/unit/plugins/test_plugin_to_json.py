from tracardi.service.plugin.service.plugin_runner import run_plugin
from tracardi.process_engine.action.v1.converters.data_to_json.plugin import ObjectToJsonAction
from tracardi.domain.profile import Profile
from tracardi.domain.event import Event, EventSession
from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventMetadata, EventTime


def test_data_to_json_plugin():
    init = {
        "to_json": "payload@dict"
    }
    payload = {
        "dict": {
            "key": "value",
            "object": {
                "embedded_key": "some_value"
            },
            "integer": 10,
            "float": 2.05,
            "null": None,
            "bool_true": True,
            "bool_false": False
        }
    }
    expected = '{"key": "value", "object": {"embedded_key": "some_value"}, "integer": 10, "float": 2.05, ' \
               '"null": null, "bool_true": true, "bool_false": false}'

    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )

    result = run_plugin(ObjectToJsonAction, init, payload, profile=Profile(id="1"), event=event)

    assert result.output.port == "payload"
    assert result.output.value == {"json": expected}
