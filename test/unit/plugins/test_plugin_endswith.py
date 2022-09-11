import pytest

from tracardi.process_engine.action.v1.ends_with_action import EndsWithAction, Config
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_should_return_true():
    init = {
        "field": "payload@name",
        "prefix": "st"
    }

    payload = {"name": "Test"}

    result = run_plugin(EndsWithAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"name": "Test"}


def test_should_return_false():
    init = {
        "field": "payload@name",
        "prefix": "test"
    }

    payload = {"name": "None"}

    result = run_plugin(EndsWithAction, init, payload)
    assert result.output.port == "false"
    assert result.output.value == {"name": "None"}


def test_empty_prefix_validation():
    with pytest.raises(ValueError):
        Config(field="payload@name", prefix="")
