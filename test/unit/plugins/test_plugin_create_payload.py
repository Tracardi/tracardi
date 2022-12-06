import json

from tracardi.process_engine.action.v1.traits.reshape_payload_action import ReshapePayloadAction
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_should_return_reshaped_value():

    reshape = {
            "rule": []
        }

    init = {
        "value": reshape,
        "default": "true"
    }

    init['value'] = json.dumps(init['value'])

    result = run_plugin(ReshapePayloadAction, init, {})
    assert result.output.port == "payload"
    assert result.output.value == reshape