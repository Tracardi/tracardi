from tracardi.domain.entity import PrimaryEntity
from tracardi.domain.entity_record import EntityRecord
from tracardi.domain.storage_record import RecordMetadata


def test_should_set_entity_record_data():
    entity = EntityRecord(
        id='1',
        profile=PrimaryEntity(id='2'),
        type="payment"
    )
    entity.set_meta_data(RecordMetadata(id="1", index="index"))
    assert entity.type == 'payment'
    assert entity.metadata.time.insert is not None

    print(entity.metadata.time.insert)
