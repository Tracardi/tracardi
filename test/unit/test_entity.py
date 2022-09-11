from typing import Optional

from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.storage_record import RecordMetadata
from tracardi.domain.value_object.storage_info import StorageInfo


def test_should_set_entity_data():
    entity = Entity(id='1')
    entity.set_meta_data(RecordMetadata(id="1", index="index"))

    assert entity.id == "1"
    assert entity.get_meta_data().id == "1"
    assert entity.get_meta_data().index == "index"


def test_should_set_entity_metadata_as_instance_attribute():
    entity = Entity(id='1')
    entity.set_meta_data(RecordMetadata(id="1", index="index"))
    assert entity.get_meta_data().id == "1"
    assert entity.get_meta_data().index == "index"

    entity1 = Entity(id='2')
    assert entity1.get_meta_data() is None


def test_should_accept_empty_meta_data():
    entity = Entity(id='1')

    assert entity.id == "1"
    assert entity.get_meta_data() is None


def test_should_return_index_less_record():
    class TestEntity(Entity):

        @staticmethod
        def storage_info() -> StorageInfo:
            return StorageInfo(
                'event',
                TestEntity,
                multi=True
            )

    entity = TestEntity(id="1")
    record = entity.to_storage_record()
    assert record.has_meta_data() is False
    assert record.get_meta_data() is None


def test_should_return_record_with_metadata():
    class TestEntity(Entity):

        @staticmethod
        def storage_info() -> StorageInfo:
            return StorageInfo(
                'event',
                TestEntity,
                multi=False
            )

    entity = TestEntity(id="1").set_meta_data(RecordMetadata(id="1", index="index"))
    record = entity.to_storage_record()
    assert record.has_meta_data() is True
    assert record.get_meta_data() is not None
    assert record.get_meta_data().index == 'index'
    assert record.get_meta_data().id == '1'


def test_should_exclude_data():
    class TestEntity(Entity):

        @staticmethod
        def storage_info() -> StorageInfo:
            return StorageInfo(
                'event',
                TestEntity,
                multi=False
            )

    entity = TestEntity(id="1").set_meta_data(RecordMetadata(id="1", index="index"))
    record = entity.to_storage_record(exclude={"id": ...})
    assert 'id' not in record


def test_should_accept_none_metadata():
    class TestEntity(Entity):

        @staticmethod
        def storage_info() -> StorageInfo:
            return StorageInfo(
                'event',
                TestEntity,
                multi=False
            )

    entity = TestEntity(id="1").set_meta_data(None)
    assert entity.has_meta_data() is False
