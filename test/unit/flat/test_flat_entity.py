import pickle

import pytest
from unittest.mock import patch

from tracardi.domain.entity import FlatEntity, change_monitor
from tracardi.domain.flat_profile import FlatProfile
from tracardi.service.change_monitoring.field_update_logger import FieldUpdateLogger
from durable_dot_dict.dotdict import DotDict


@pytest.fixture
def flat_entity():
    return FlatEntity({'key': 'value'})


def test_init(flat_entity):
    assert isinstance(flat_entity, FlatEntity)
    assert flat_entity['key'] == 'value'
    assert flat_entity._metadata is None
    assert flat_entity._changes is None


def test_changes_method():
    flat_entity = FlatProfile({'key': 'value'})
    assert not flat_entity.has_changes()



def test_serialization():
    fp = FlatProfile({'key': 'value'})
    fp.monitor_changes(True)
    fp['test'] = 1

    serialized = pickle.dumps(fp)
    deserialized: FlatProfile = pickle.loads(serialized)
    print(deserialized)
    assert deserialized.has_changes()

    fp.fill_changed_fields()


def test_getstate(flat_entity):
    flat_entity._metadata = {'some': 'metadata'}
    state = flat_entity.__getstate__()
    assert state['_data'] == {'key': 'value'}
    assert state['_metadata'] == {'some': 'metadata'}


def test_setstate():
    state = {
        '_data': {'key': 'value'},
        '_metadata': {'some': 'metadata'},
        '_changes': []
    }
    entity = FlatEntity({})
    entity.__setstate__(state)
    assert entity['key'] == 'value'
    assert entity._metadata == {'some': 'metadata'}
    assert entity._changes == []


def test_setstate_no_metadata():
    state = {
        '_data': {'key': 'value'}
    }
    entity = FlatEntity({})
    entity.__setstate__(state)
    assert entity['key'] == 'value'
    assert entity._metadata is None
    assert entity._changes is None


def test_setitem(flat_entity):
    with change_monitor(flat_entity):
        with patch.object(flat_entity._changes, 'add') as mock_add:
            flat_entity['new_key'] = 'new_value'
            assert flat_entity['new_key'] == 'new_value'
            mock_add.assert_called_once()


def test_setitem_ignored_keys(flat_entity):
    with change_monitor(flat_entity):
        with patch.object(flat_entity._changes, 'add') as mock_add:
            flat_entity['metadata.fields'] = 'some_value'
            assert flat_entity['metadata.fields'] == 'some_value'
            mock_add.assert_called_once()

        with patch.object(flat_entity._changes, 'add') as mock_add:
            flat_entity['operation'] = 'some_operation'
            assert flat_entity['operation'] == 'some_operation'
            mock_add.assert_called_once()


def test_inheritance(flat_entity):
    assert isinstance(flat_entity, DotDict)


def test_changes_attribute(flat_entity):
    with change_monitor(flat_entity):
        assert hasattr(flat_entity, '_changes')
        assert isinstance(flat_entity._changes, FieldUpdateLogger)
    assert flat_entity._changes is None


def test_changes(flat_entity):
    with change_monitor(flat_entity):
        assert not flat_entity._changes.changes()
        flat_entity['a'] = 1
        assert bool(flat_entity._changes.changes())

        assert list(flat_entity._changes.changes())[0][0] == 'a'
        assert len(flat_entity._changes.changes()) == 1
        # Now lets test is change with the same value makes the change log modifications. It should not.
        flat_entity['key'] = 'value'
        # Still no new changes
        assert len(flat_entity._changes.changes()) == 1
        assert not flat_entity._changes._changes.exists('key')

        # Now lets change the value
        flat_entity['key'] = 'value1'
        # Still no new changes
        assert len(flat_entity._changes.changes()) == 2
        assert flat_entity._changes._changes.exists('key')


def test_embedded_changes(flat_entity):
    flat_entity['a.b.c'] = False
    with change_monitor(flat_entity):
        flat_entity['a.b.c'] = False
        assert not flat_entity._changes._changes
        flat_entity['a.b.c'] = True
        assert bool(flat_entity._changes._changes)
        assert flat_entity._changes._changes.get_change('a.b.c')[1] is False  # has old value


# TODO
def test_multiple_changes_that_cancel_themselves(flat_entity):
    flat_entity = FlatEntity({'field': 'a'})
    with change_monitor(flat_entity):
        flat_entity['field'] = 'b'
        print(flat_entity.get_change_logger().changes())
        flat_entity['field'] = 'a'
        print(flat_entity.get_change_logger().changes())


# TODO
def test_appending_changes():
    flat_entity = FlatEntity({'ids': []})
    with change_monitor(flat_entity):
        flat_entity['ids'].append(1)
        print(flat_entity.get_change_logger().changes())
