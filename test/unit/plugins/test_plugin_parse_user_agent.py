from tracardi.domain.session import Session, SessionMetadata
from tracardi.process_engine.action.v1.detect_client_agent_action import DetectClientAgentAction
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_plugin_parse_user_agent():
    init = {
        "agent": "session@context.userAgent",
    }

    payload = {}

    result = run_plugin(DetectClientAgentAction, init, payload, session=Session(id="1", context={
        "userAgent": "Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405"
    }, metadata=SessionMetadata()))

    assert result.output.value['device']['model']['name'] == 'iPad'
    assert result.output.value['device']['model']['brand']['name'] == 'Apple'
    assert result.output.value['device']['model']['type'] == 'tablet'
    assert result.output.value['device']['os']['name'] == 'iOS'
    assert result.output.value['device']['os']['version'] == '3.2.1'
    assert result.output.value['device']['client']['type'] == 'browser'
    assert result.output.value['device']['client']['name'] == 'Mobile Safari'
    assert result.output.value['device']['type']['mobile'] is True
    assert result.output.value['device']['type']['desktop'] is False


