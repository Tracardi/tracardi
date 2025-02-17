from tracardi.domain.flat_session import FlatSession
from tracardi.service.plugin.service.plugin_runner import run_plugin
from tracardi.process_engine.action.v1.strings.url_parser.plugin import ParseURLParameters


def test_url_plugin_fail():
    init = {
        "url": 'session@context.page.url'
    }
    payload = {}
    session = FlatSession.new(id='1')
    session['context'] = {
        'page': {
            'none': "http://test.url/path/?param=1#hash"
        }
    }

    try:
        run_plugin(ParseURLParameters, init, payload, session=session)
        assert False
    except KeyError:
        assert True


def test_url_parser_plugin_ok():
    init = {
        "url": 'session@context.page.url'
    }
    payload = {}
    session = FlatSession.new(
        id='1')
    session['context'] = {
        'page': {
            'url': "http://test.url/path/?param=1#hash"
        }
    }

    result = run_plugin(ParseURLParameters, init, payload, session=session)
    assert result.output.value == {'url': 'http://test.url/path/?param=1#hash', 'scheme': 'http',
                                   'hostname': 'test.url', 'path': '/path/', 'query': 'param=1',
                                   'params': {'param': '1'}, 'fragment': 'hash'}
