import pytest

from tracardi.service.change_monitoring.field_change_monitor import FieldTimestampMonitor


def test_setting_field_updates_profile_and_logs_change():
    flat_profile = {'field1': 'value1', 'field2': 'value2'}
    monitor = FieldTimestampMonitor(flat_profile, 'type', 'profile_id')
    monitor['field1'] = 'new_value'
    assert monitor['field1'] == 'new_value'

    assert monitor.get_timestamps_list()[0]['id'] == 'field1'
    assert monitor.get_timestamps_list()[0]['type'] == 'type'
    assert monitor.get_timestamps_list()[0]['profile_id'] == 'profile_id'
    assert monitor.get_timestamps_list()[0]['source_id'] is None
    assert monitor.get_timestamps_list()[0]['session_id'] is None
    assert monitor.get_timestamps_list()[0]['field'] == 'field1'
    assert monitor.get_timestamps_list()[0]['value'] == 'new_value'


def test_retrieving_field_returns_correct_value():
    flat_profile = {'field1': 'value1', 'field2': 'value2'}
    monitor = FieldTimestampMonitor(flat_profile, 'type', 'profile_id')
    assert monitor['field1'] == 'value1'


def test_retrieving_nonexistent_field_raises_key_error():
    flat_profile = {'field1': 'value1', 'field2': 'value2'}
    monitor = FieldTimestampMonitor(flat_profile, 'type', "profile_id")
    with pytest.raises(KeyError):
        monitor['field3']
