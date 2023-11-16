from tracardi.domain.entity import Entity
from tracardi.service.change_monitoring.field_change_monitor import FieldChangeLogManager


def test_append_log_entry():
    session = Entity(id="0")
    source = Entity(id="1")

    log_manager = FieldChangeLogManager()
    log_manager.append("type1", 'profile_id', 'event_id', session.id, source.id, "field1", "value1")

    log = log_manager.get_log()
    assert len(log) == 1
    assert log[0]['type'] == "type1"
    assert log[0]['field'] == "field1"
    assert log[0]['value'] == "value1"


def test_none_session_and_source():
    log_manager = FieldChangeLogManager()
    log_manager.append("type1", None, None, None, None, "field1", "value1")

    log = log_manager.get_log()
    assert len(log) == 1
    assert log[0]['type'] == "type1"
    assert log[0]['field'] == "field1"
    assert log[0]['value'] == "value1"


def test_empty_session_and_source():
    session = Entity(id="0")
    source = Entity(id="1")

    log_manager = FieldChangeLogManager()
    log_manager.append("type1", 'profile_id', 'event_id', session.id, source.id, "field1", "value1")
    log_manager.append("type2", None, None, None, None, "field2", "value2")

    log = log_manager.get_log()
    assert len(log) == 2
    assert log[0]['type'] == "type1"
    assert log[0]['field'] == "field1"
    assert log[0]['value'] == "value1"
    assert log[0]['profile_id'] == "profile_id"

    assert log[1]['type'] == "type2"
    assert log[1]['field'] == "field2"
    assert log[1]['value'] == "value2"
    assert log[1]['profile_id'] is None


def test_none_type_field_value():

    log_manager = FieldChangeLogManager()
    log_manager.append(None, None, None, None, None, None, None)

    log = log_manager.get_log()
    assert len(log) == 1
    assert log[0]['type'] is None
    assert log[0]['field'] is None
    assert log[0]['value'] is None

    log_manager.get_log()
