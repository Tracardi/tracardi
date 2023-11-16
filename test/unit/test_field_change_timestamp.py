from tracardi.service.change_monitoring.field_change_monitor import FieldChangeTimestampManager


def test_append_valid_input_parameters():
    manager = FieldChangeTimestampManager()
    manager.append(type="type", session_id="session_id", source_id="source_id", field="field", value="value")
    log = manager.get_log()
    assert len(log) == 1
    assert len(log["type"]) == 1
    assert log["type"]["field"]["id"] == "field"
    assert log["type"]["field"]["type"] == "type"
    assert log["type"]["field"]["source_id"] == "source_id"
    assert log["type"]["field"]["session_id"] == "session_id"
    assert log["type"]["field"]["field"] == "field"
    assert log["type"]["field"]["value"] == "value"


def test_get_log():
    manager = FieldChangeTimestampManager()
    log = manager.get_log()
    assert log == {}


def test_get_list():
    manager = FieldChangeTimestampManager()
    log_list = manager.get_list()
    assert log_list == []
