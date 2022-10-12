from tracardi.process_engine.action.v1.sort_dictionary import SortedDictAction
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_sort_dictionary_plugin():
    properties = {"data": {"first": 1, "second": 2, "fifth": 5, "third": 3}}
    init = dict(
        data='event@properties.data',
        direction='asc',
    )

    result = run_plugin(SortedDictAction, init, properties)
    assert result.output.value == {"result": [["first", 1], ["second", 2], ["third", 3], ["fifth", 5]]}
