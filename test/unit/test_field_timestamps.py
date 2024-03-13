import pytest

from tracardi.service.change_monitoring.field_change_monitor import FieldTimestampMonitor


def test_setting_field_updates_profile_and_logs_change():
    flat_profile = {'field1': 'value1', 'field2': 'value2'}
    monitor = FieldTimestampMonitor(flat_profile, 'type', 'profile_id', 'event_id')
    monitor['field1'] = 'new_value'
    assert monitor['field1'] == 'new_value'

    assert monitor.get_timestamps_list()[0]['id'] == 'field1:profile_id'
    assert monitor.get_timestamps_list()[0]['type'] == 'type'
    assert monitor.get_timestamps_list()[0]['profile_id'] == 'profile_id'
    assert monitor.get_timestamps_list()[0]['event_id'] == 'event_id'
    assert monitor.get_timestamps_list()[0]['source_id'] is None
    assert monitor.get_timestamps_list()[0]['session_id'] is None
    assert monitor.get_timestamps_list()[0]['field'] == 'field1'
    assert monitor.get_timestamps_list()[0]['value'] == 'new_value'


def test_retrieving_field_returns_correct_value():
    flat_profile = {'field1': 'value1', 'field2': 'value2'}
    monitor = FieldTimestampMonitor(flat_profile, 'type', 'profile_id', 'event_id')
    assert monitor['field1'] == 'value1'


def test_retrieving_nonexistent_field_raises_key_error():
    flat_profile = {'field1': 'value1', 'field2': 'value2'}
    monitor = FieldTimestampMonitor(flat_profile, 'type', "profile_id", 'event_id')
    with pytest.raises(KeyError):
        x = monitor['field3']


def test_adding_monitors():
    flat_profile1 = {'field1': 'value1', 'field2': 'value2'}
    monitor1 = FieldTimestampMonitor(flat_profile1, 'type', 'profile_id', 'event_id1')
    monitor1['field1'] = 'value12'

    flat_profile2 = {'field2': 'value22', 'field3': 'value3'}
    monitor2 = FieldTimestampMonitor(flat_profile2, 'type', 'profile_id', 'event_id1')
    monitor2['field2'] = 'value12'

    assert 1 == len(list(monitor1.get_timestamps_log().get_timestamps()))
    assert 1 == len(list(monitor2.get_timestamps_log().get_timestamps()))

    monitor3 = monitor1 + monitor2
    assert 2 == len(list(monitor3.get_timestamps_log().get_timestamps()))


