import pytest

from tracardi.service.storage.speedb.rocksdb_clinet import RocksDbClient

db = RocksDbClient('test.db')
db.create_storage()

def test_returns_true_if_storage_path_exists():
    assert db.check_storage() is True


def test_add_delete_unique_record():
    key = "key1"
    value = "value1"
    db.add_record(key, value)
    assert db[key] == value
    db.delete_record(key)
    with pytest.raises(KeyError):
        assert db[key] == value


def test_override_record():
    key = "key1"
    value = "value1"
    db.add_record(key, value)
    value = "value2"
    db.add_record(key, value)
    assert db[key] == value


def test_iterate():
    db.destroy_storage()
    db.create_storage()
    db.add_record("1", "value1")
    db.add_record("2", "value2")
    for k,v in db.get_all_records():
        assert k in ['1','2']
        assert v in ['value1', 'value2']