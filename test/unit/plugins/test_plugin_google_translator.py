import pytest

from tracardi.process_engine.action.v1.connectors.google.translate.plugin import GoogleTranslateAction
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_should_translate_given_text():
    init = {
        "text_to_translate": "veritas lux mea",
        "source_language": "la"
    }

    payload = None

    result = run_plugin(GoogleTranslateAction, init, payload)

    assert result.output.port == "translation"
    assert result.output.value == {"translation": "The truth is my light"}


def test_should_raise_value_error():
    with pytest.raises(ValueError):
        init = {
            "text_to_translate": "veritas lux mea",
            "source_language": "test-language"
        }
        payload = None
        run_plugin(GoogleTranslateAction, init, payload)


def test_to_check_source_language_empty_field_validator():
    with pytest.raises(ValueError):
        init = {
            "text_to_translate": "veritas lux mea",
            "source_language": ""
        }
        payload = None
        run_plugin(GoogleTranslateAction, init, payload)


def test_to_check_source_language_type_validator():
    with pytest.raises(ValueError):
        init = {
            "text_to_translate": "veritas lux mea",
            "source_language": 1
        }
        payload = None
        run_plugin(GoogleTranslateAction, init, payload)
