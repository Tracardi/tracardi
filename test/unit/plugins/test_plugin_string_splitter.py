from tracardi.service.plugin.service.plugin_runner import run_plugin

from tracardi.process_engine.action.v1.strings.string_splitter.plugin import SplitterAction


def test_string_splitter_plugin():
    payload = {"string": 'a,b,c'}
    init = dict(
        string='payload@string',
        delimiter=',',
    )

    result = run_plugin(SplitterAction, init, payload)
    assert result.output.value == {'result': ['a', 'b', 'c']}
