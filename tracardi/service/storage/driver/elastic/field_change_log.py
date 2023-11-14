from typing import Optional

from tracardi.domain.entity_record import EntityRecord
from tracardi.domain.storage_record import StorageRecords
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.factory import storage_manager


async def load(entity_id) -> Optional[EntityRecord]:
    return EntityRecord.create(await storage_manager("field-change-log").load(entity_id))


async def load_by_field(field: str) -> StorageRecords:
    field_value_pairs = [
        ('field', field)
    ]
    return await storage_manager("field-change-log").load_by_values(field_value_pairs)


async def load_by_type_and_field(type: str, field: str) -> StorageRecords:
    field_value_pairs = [
        ('type', type),
        ('field', field)
    ]
    return await storage_manager("field-change-log").load_by_values(field_value_pairs)


async def upsert(data: list) -> BulkInsertResult:
    return await storage_manager("field-change-log").upsert(data)


async def refresh():
    return await storage_manager("field-change-log").refresh()


async def flush():
    return await storage_manager("field-change-log").flush()


async def count(query: dict = None):
    return await storage_manager("field-change-log").count(query)
