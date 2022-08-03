from tracardi.domain.entity_record import EntityRecord
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor, storage_manager


async def load_by_id(entity_id) -> EntityRecord:
    entity = Entity(id=entity_id)
    return await StorageFor(entity).index("entity").load(EntityRecord)  # type: EntityRecord


async def upsert(entity: EntityRecord) -> BulkInsertResult:
    return await StorageFor(entity).index().save()


async def refresh():
    return await storage_manager('entity').refresh()


async def flush():
    return await storage_manager('entity').flush()
