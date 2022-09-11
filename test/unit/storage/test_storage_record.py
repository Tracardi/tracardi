from tracardi.domain.storage_record import StorageRecord, RecordMetadata


def test_should_assign_and_read_values():
    record = StorageRecord(test="sss")
    assert isinstance(record, dict)
    assert record['test'] == 'sss'
    del record['test']
    assert 'test' not in record

    record = StorageRecord(**{"test": "sss"})
    assert isinstance(record, dict)
    assert record['test'] == 'sss'
    del record['test']
    assert 'test' not in record


def test_should_assign_meta_data():
    record = StorageRecord(test="sss")
    record.set_meta_data(RecordMetadata(id="test", index="index"))
    assert record.get_meta_data().id == "test"
    assert record.get_meta_data().index == "index"
