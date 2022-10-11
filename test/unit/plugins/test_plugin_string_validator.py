import pytest
import random
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event, EventSession
from tracardi.domain.event_metadata import EventMetadata, EventTime
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.profile_traits import ProfileTraits
from tracardi.service.plugin.service.plugin_runner import run_plugin

from tracardi.process_engine.action.v1.strings.string_validator.plugin import StringValidatorAction


@pytest.mark.email
def test_email():
    import random
    import string
    number = 0

    def random_char(char_num):
        return ''.join(random.choice(string.ascii_letters) for _ in range(char_num))

    while not number == 10:
        a = random_char(12) + "@" + random_char(5) + "." + random_char(3)
        number += 1
        init = {'validator': "email",
                'data': a}
        payload = {}
        plugin = run_plugin(StringValidatorAction, init, payload)
        result = plugin.output
        assert result.port == 'valid'
        assert result.value == payload


def test_url():
    init = {'validator': "url",
            'data': f"https://www.polska.com/api/e/w/2"}
    plugin = run_plugin(StringValidatorAction, init, {})
    result = plugin.output
    assert result.port == 'valid'
    assert result.value == {}


@pytest.mark.date
def test_date():
    a = 0
    while not a == 1000:
        c = random.randint(1, 12)
        if c == 2:
            b = random.randint(1, 28)
        else:
            b = random.randint(1, 30)
        d = random.randint(1600, 2021)
        a += 1
        init = {'validator': "date",
                'data': f"{b}-{c}-{d}"}
        plugin = run_plugin(StringValidatorAction, init, {})
        result = plugin.output
        assert result.port == 'valid'
        assert result.value == {}


def test_int():
    a = 0
    while not a == 1000:
        c = random.randint(1, 100000)
        a += 1
        init = {'validator': "int",
                'data': c}
        plugin = run_plugin(StringValidatorAction, init, {})
        result = plugin.output
        assert result.port == 'valid'
        assert result.value == {}


def test_float():
    a = 0
    while not a == 1000:
        c = random.uniform(1.0, 100000.0)
        a += 1
        init = {'validator': "float",
                'data': c}
        plugin = run_plugin(StringValidatorAction, init, {})
        result = plugin.output
        assert result.port == 'valid'
        assert result.value == {}


def test_timer():
    a = 0
    while not a == 1000:
        c = random.randint(1, 23)
        d = random.randint(1, 59)
        if d < 10:
            d = "0" + str(d)

        a += 1
        init = {'validator': "time",
                'data': f"{c}:{d}"}
        plugin = run_plugin(StringValidatorAction, init, {})
        result = plugin.output
        assert result.port == 'valid'
        assert result.value == {}


def test_ean():
    a = "5901234123457"
    init = {'validator': "ean",
            'data': a}
    plugin = run_plugin(StringValidatorAction, init, {})
    result = plugin.output
    assert result.port == 'valid'
    assert result.value == {}


def test_number_phone():
    a = 0
    while not a == 1000:
        d = random.randint(1, 999)
        if d < 10:
            d = '+0' + str(d)
        else:
            d = '+' + str(d)

        c = random.randint(1000000, 999999999)
        a += 1
        init = {'validator': "number_phone",
                'data': f"{d}{c}"}
        plugin = run_plugin(StringValidatorAction, init, {})

        result = plugin.output
        assert result.port == 'valid'
        assert result.value == {}


@pytest.mark.ip
def test_ip():
    a = 0
    while not a == 1000:
        b = random.randint(1, 255)
        c = random.randint(1, 255)
        d = random.randint(1, 255)
        e = random.randint(1, 255)
        a += 1
        init = {'validator': "ipv4",
                'data': f"{b}.{c}.{d}.{e}"}
        plugin = run_plugin(StringValidatorAction, init, {})
        result = plugin.output
        assert result.port == 'valid'
        assert result.value == {}


def test_string_validator_plugin():
    payload = {"data": "my@email.com"}
    init = {
        'validator': 'email',
        'data': "payload@data"
    }

    plugin = run_plugin(StringValidatorAction, init, payload)

    result = plugin.output
    assert result.port == 'valid'
    assert result.value == payload


def test_string_validator_plugin_fails():
    init = {
        "data": "event@id",
        "validator": "time"
    }
    payload = {}
    profile = Profile(id="profile-id", traits=ProfileTraits(public={"test": "new test"}))
    event = Event(
        id='event-id',
        type='event-type',
        metadata=EventMetadata(time=EventTime()),
        session=EventSession(id='session-id'),
        source=Entity(id='source-id')
    )
    plugin = run_plugin(StringValidatorAction, init, payload,
                        profile, None, event)
    result = plugin.output
    assert result.port == 'invalid'
    assert result.value == payload
