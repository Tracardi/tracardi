from tracardi.process_engine.action.v1.end_action import EndAction
from tracardi.domain.profile import Profile
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_plugin_end():
    init = {}

    payload = {}

    result = run_plugin(EndAction, init, payload, profile=Profile(id="1"))
    assert result.output is None



