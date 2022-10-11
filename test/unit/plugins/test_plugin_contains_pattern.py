import pytest
from pydantic import ValidationError

from tracardi.process_engine.action.v1.operations.contains_pattern.plugin import ContainsPatternAction, Config
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_should_not_return_anything_if_no_match():
    init = {
        "field": "ala ma kota",
        "pattern": "email"
    }

    payload = {"field": "test@test.com"}

    result = run_plugin(ContainsPatternAction, init, payload)

    assert result.output.port == "false"

    init = {
        "field": "ala ma kota",
        "pattern": "all"
    }

    payload = {"field": "test@test.com"}

    result = run_plugin(ContainsPatternAction, init, payload)

    assert result.output.port == "false"


def test_should_return_email():
    init = {
        "field": "payload@field",
        "pattern": "email"
    }

    payload = {"field": "test@test.com"}

    result = run_plugin(ContainsPatternAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"email": ["test@test.com"]}


def test_should_return_ip():
    init = {
        "field": "payload@field",
        "pattern": "ip"
    }

    payload = {"field": "192.168.0.1"}

    result = run_plugin(ContainsPatternAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"ip": ["192.168.0.1"]}


def test_should_return_date():
    init = {
        "field": "payload@field",
        "pattern": "date"
    }

    payload = {"field": "15-03-2022"}

    result = run_plugin(ContainsPatternAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"date": ["15-03-2022"]}


def test_should_return_url():
    init = {
        "field": "payload@field",
        "pattern": "url"
    }

    payload = {"field": "https://www.test.com"}

    result = run_plugin(ContainsPatternAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"url": ["https://www.test.com"]}


def test_should_return_all_patterns():
    init = {
        "field": "payload@field",
        "pattern": "all"
    }

    payload = {"field": "https://www.test.com, 192.168.0.1, 20-10-2016, 20-10-2017, test@test.com"}

    result = run_plugin(ContainsPatternAction, init, payload)
    assert result.output.port == "true"
    assert result.output.value == {"email": ['test@test.com'],
                                   "ip": ["192.168.0.1"],
                                   "date": ["20-10-2016", "20-10-2017"],
                                   "url": ["https://www.test.com"]}


def test_should_check_empty_pattern_field_validation():
    with pytest.raises(ValueError):
        Config(field="test@test.com", pattern="")


def test_field_data_type_exception():
    init = {
        "field": "payload@field",
        "pattern": "mail"
    }

    payload = {"field": 1}

    with pytest.raises(ValidationError):
        run_plugin(ContainsPatternAction, init, payload)
