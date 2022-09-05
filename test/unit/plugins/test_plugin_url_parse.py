import asyncio
from tracardi.domain.session import Session, SessionMetadata
from tracardi.process_engine.action.v1.strings.url_parser.plugin import ParseURLParameters
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_plugin_url_parser_ok():
    init = {
        "url": 'session@context.page.url'
    }

    payload = {}

    session = Session(
        id='1',
        metadata=SessionMetadata(),
        context={
            'page': {
                'url': "http://test.url/path/?param=1#hash"
            }
        }
    )
    result = run_plugin(ParseURLParameters, init, payload, session=session)
    result = result.output

    assert result.value['url'] == "http://test.url/path/?param=1#hash"
    assert result.value['scheme'] == 'http'
    assert result.value['hostname'] == 'test.url'
    assert result.value['path'] == '/path/'
    assert result.value['query'] == 'param=1'
    assert result.value['params'] == {'param': '1'}
    assert result.value['fragment'] == 'hash'


def test_plugin_url_parser_fail():
    init = {
        "url": 'session@context.page.url'
    }

    payload = {}

    session = Session(
        id='1',
        metadata=SessionMetadata(),
        context={
            'page': {
                'no-key': "http://test.url/path/?param=1#hash"  # Incorrect key
            }
        }
    )

    try:
        run_plugin(ParseURLParameters, init, payload, session=session)
        assert False
    except KeyError:
        assert True
