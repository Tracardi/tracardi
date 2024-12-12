from tracardi.service.change_monitoring.field_update_logger import FieldUpdateLogger
from time import sleep, time


def test_positive_patch():
    logger = FieldUpdateLogger()

    logger.add("a", 1, None, time())
    assert logger.get("b", None) is None
    assert isinstance(logger.get('a', None), list)

    timestamp = logger.timestamp("a")
    logger.add("a", 1, 1, time())
    # No change
    assert timestamp == logger.timestamp("a")

    logger.add("a", 2, 1, time())
    # Change
    assert timestamp != logger.timestamp("a")


def test_init():
    logger = FieldUpdateLogger()
    assert not logger._changes


def test_add_new_field():
    logger = FieldUpdateLogger()
    logger.add('field1', 'value1', None, time())
    assert len(logger._changes) == 1
    assert isinstance(logger._changes['field1'][0], float)
    assert logger._changes['field1'][1] is None


def test_add_existing_field_same_value():
    logger = FieldUpdateLogger()
    logger.add('field1', 'value1', None, time())
    initial_timestamp = logger._changes['field1'][0]
    sleep(0.01)  # Ensure some time passes
    logger.add('field1', 'value1', 'value1', time())
    assert len(logger._changes) == 1
    assert logger._changes['field1'][0] == initial_timestamp


def test_add_existing_field_different_value():
    logger = FieldUpdateLogger()
    logger.add('field1', 'value1', None, time())
    initial_timestamp = logger._changes['field1'][0]
    sleep(0.01)  # Ensure some time passes
    logger.add('field1', 'value2', 'value1', time())
    assert len(logger._changes) == 1
    assert logger._changes['field1'][0] > initial_timestamp
    assert logger._changes['field1'][1] == 'value1'


def test_timestamp():
    logger = FieldUpdateLogger()
    logger.add('field1', 'value1', None, time())
    assert isinstance(logger.timestamp('field1'), float)
    assert logger.timestamp('non_existent_field') is None


def test_changes():
    logger = FieldUpdateLogger()
    logger.add('field1', 'value1', None, time())
    logger.add('field2', 'value2', None, time())
    changes = dict(logger.changes())
    assert len(changes) == 2
    assert all(isinstance(v[0], float) and v[1] is None for v in changes.values())


def test_multiple_updates():
    logger = FieldUpdateLogger()
    logger.add('field1', 'value1', None, time())
    sleep(0.01)
    logger.add('field1', 'value2', 'value1')
    sleep(0.01)
    logger.add('field1', 'value3', 'value2')
    assert len(logger._changes) == 1
    assert logger._changes['field1'][1] == 'value2'


def test_add_multiple_fields():
    logger = FieldUpdateLogger()
    logger.add('field1', 'value1', None, time())
    logger.add('field2', 'value2', None, time())
    logger.add('field3', 'value3', None, time())
    assert len(logger._changes) == 3
    assert all(isinstance(v[0], float) and v[1] is None for _, v in logger.changes())


