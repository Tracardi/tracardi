import pytest

from tracardi.process_engine.action.v1.operations.contains_pattern.plugin import ContainsPatternAction, WrongFieldTypeError, Config
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_should_return_email():
    init = {
        "field": "payload@field",
        "pattern": "email"
    }

    payload = {"field": "test@test.com"}

    result = run_plugin(ContainsPatternAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"found": "email"}


def test_should_return_ip():
    init = {
        "field": "payload@field",
        "pattern": "ip"
    }

    payload = {"field": "192.168.0.1"}

    result = run_plugin(ContainsPatternAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"found": "ip"}


def test_should_return_date():
    init = {
        "field": "payload@field",
        "pattern": "date"
    }

    payload = {"field": "15-03-2022"}

    result = run_plugin(ContainsPatternAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"found": "date"}


def test_should_return_url():
    init = {
        "field": "payload@field",
        "pattern": "url"
    }

    payload = {"field": "https://www.test.com"}

    result = run_plugin(ContainsPatternAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"found": "url"}


def test_should_return_all_patterns():
    init = {
        "field": "payload@field",
        "pattern": "all"
    }

    payload = {"field": "https://www.test.com, 192.168.0.1, 20-10-2016, test@test.com"}

    result = run_plugin(ContainsPatternAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"found": ['email', 'ip', 'url', 'date']}


def test_should_check_empty_pattern_field_validation():
    with pytest.raises(ValueError):
        Config(field="test@test.com", pattern="")


def test_field_data_type_exception():
    init = {
        "field": "payload@field",
        "pattern": "mail"
    }

    payload = {"field": 1}

    with pytest.raises(WrongFieldTypeError):
        run_plugin(ContainsPatternAction, init, payload)