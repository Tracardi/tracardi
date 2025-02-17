from tracardi.domain.flat_session import FlatSession
from tracardi.process_engine.action.v1.new_visit_action import NewVisitAction
from tracardi.service.plugin.service.plugin_runner import run_plugin


def test_plugin_new_visit_true():
    init = {}
    payload = {}
    session = FlatSession.new(id="1")
    session.set_new()

    result = run_plugin(NewVisitAction, init, payload, session=session)
    assert result.output.value == payload
    assert result.output.port == 'true'


def test_plugin_new_visit_false():
    init = {}
    payload = {}
    session = FlatSession.new(id="1")
    session.set_new(False)

    result = run_plugin(NewVisitAction, init, payload, session=session)
    assert result.output.value == payload
    assert result.output.port == 'false'
