from tracardi.process_engine.action.v1.converters.base64.decode.plugin import Base64DecodeAction
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_decodes_plain_text_from_base64():
    init = {
        'source': 'payload@base64',
        'target_encoding': 'utf-8',
    }
    payload = {
        'base64': 'aGVsbG8gdHJhY2FyZGk=',
    }
    result = run_plugin(Base64DecodeAction, init, payload)

    assert result.output.port == 'payload'
    assert result.output.value == {'text': 'hello tracardi'}


def test_decodes_unpadded_base64():
    init = {
        'source': 'payload@base64',
        'target_encoding': 'utf-8',
    }
    payload = {
        'base64': 'aGVsbG8gdHJhY2FyZGk',
    }

    result = run_plugin(Base64DecodeAction, init, payload)

    assert result.output.port == 'payload'
    assert result.output.value == {'text': 'hello tracardi'}

def test_decodes_plain_text_with_target_encoding():
    init = {
        'source': 'payload@base64',
        'target_encoding': 'utf-16-le',
    }
    payload = {
        'base64': 'aABlAGwAbABvACAAdAByAGEAYwBhAHIAZABpAA==',
    }
    result = run_plugin(Base64DecodeAction, init, payload)

    assert result.output.port == 'payload'
    assert result.output.value == {'text': 'hello tracardi'}
