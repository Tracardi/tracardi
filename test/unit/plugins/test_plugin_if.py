from tracardi.process_engine.action.v1.if_action import IfAction
from tracardi.domain.profile import Profile
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_plugin_if_true():
    init = {
        "condition": 'profile@id==\"1\"'
    }
    payload = {}

    result = run_plugin(IfAction, init, payload, profile=Profile(id="1"))
    assert result.output.value == payload
    assert result.output.port == 'true'


def test_plugin_if_false():
    init = {
        "condition": 'profile@id!=\"1\"'
    }
    payload = {"payload": 1}

    result = run_plugin(IfAction, init, payload, profile=Profile(id="1"))
    assert result.output.value == {"payload": 1}
    assert result.output.port == 'false'


def test_plugin_if_fail_1():
    init = {
        "condition": None
    }
    payload = {"payload": 1}

    try:
        run_plugin(IfAction, init, payload, profile=Profile(id="1"))
        assert False
    except ValueError:
        assert True


def test_plugin_if_fail_2():
    init = {}
    payload = {"payload": 1}

    try:
        run_plugin(IfAction, init, payload, profile=Profile(id="1"))
        assert False
    except ValueError:
        assert True
