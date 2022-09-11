from tracardi.service.plugin.service.plugin_runner import run_plugin
from tracardi.process_engine.action.v1.strings.string_operations.plugin import StringPropertiesActions
from tracardi.domain.profile import Profile
from tracardi.domain.event import Event, EventSession
from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventMetadata, EventTime


def test_should_work():
    init = {
        "string": "payload@text"
    }
    payload = {
        "text": " Lorem ipsum dolor sit amet 0 \ "
    }

    event = Event(
        id='1',
        type='text',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='1'),
        source=Entity(id='1')
    )

    result = run_plugin(StringPropertiesActions, init, payload, profile=Profile(id="1"), event=event)

    expected = {
        'capitalize': ' lorem ipsum dolor sit amet 0 \\ ',
        'casefold': ' lorem ipsum dolor sit amet 0 \\ ',
        'encode': b' Lorem ipsum dolor sit amet 0 \\ ',
        'isalnum': False,
        'isalpha': False,
        'isascii': True,
        'isdecimal': False,
        'isdigit': False,
        'isidentifier': False,
        'islower': False,
        'isnumeric': False,
        'isprintable': True,
        'isspace': False,
        'istitle': False,
        'isupper': False,
        'lower': ' lorem ipsum dolor sit amet 0 \\ ',
        'lstrip': 'Lorem ipsum dolor sit amet 0 \\ ',
        'swapcase': ' lOREM IPSUM DOLOR SIT AMET 0 \\ ',
        'title': ' Lorem Ipsum Dolor Sit Amet 0 \\ ',
        'upper': ' LOREM IPSUM DOLOR SIT AMET 0 \\ '
    }

    assert result.output.value == expected
