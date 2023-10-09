from tracardi.service.plugin.service.plugin_runner import run_plugin

from tracardi.process_engine.action.v1.strings.string_stripper.plugin import StringStripper


def test_string_stripper_plugin():
    payload = {"string": "Hello, World!"}
    init = dict(
        string="payload@string",
        to_remove="Ho",
    )
    result = run_plugin(StringStripper, init, payload)
    assert result.output.value == {"value": "ell, Wrld!"}
