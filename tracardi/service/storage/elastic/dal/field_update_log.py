from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.elastic.driver.factory import storage_manager


async def load_by_type(type: str) -> dict:
    field_value_pairs = [
        ('type', type)
    ]
    result = await storage_manager("field-update-log").load_by_values(field_value_pairs)
    return result.dict()


async def upsert(data: list) -> BulkInsertResult:
    return await storage_manager("field-update-log").upsert(data)

# Not used - TODO Check
# async def refresh():
#     return await storage_manager("field-update-log").refresh()
#
#
# async def flush():
#     return await storage_manager("field-update-log").flush()
#
#
# async def count(query: dict = None) -> dict:
#     return await storage_manager("field-update-log").count(query)
#
# async def load(entity_id) -> Optional[EntityRecord]:
#     return EntityRecord.create(await storage_manager("field-update-log").load(entity_id))
