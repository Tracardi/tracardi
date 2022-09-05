import pytest

from tracardi.process_engine.action.v1.contains_string_action import ContainsStringAction, Config, WrongFieldTypeError
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_should_return_true():
    init = {
        "field": "payload@field",
        "substring": "contains"
    }

    payload = {"field": "Test to check if field contains string"}

    result = run_plugin(ContainsStringAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"field": "Test to check if field contains string"}


def test_should_return_false():
    init = {
        "field": "payload@field",
        "substring": "test"
    }

    payload = {"field": "Test to check if field doesnt contains string"}

    result = run_plugin(ContainsStringAction, init, payload)
    assert result.output.port == "false"
    assert result.output.value == {"field": "Test to check if field doesnt contains string"}


def test_empty_prefix_validation():
    with pytest.raises(ValueError):
        Config(field="payload@name", prefix="")


def test_field_data_type_exception():
    init = {
        "field": "payload@field",
        "substring": "Substring test"
    }

    payload = {"field": 1}

    with pytest.raises(WrongFieldTypeError):
        run_plugin(ContainsStringAction, init, payload)


