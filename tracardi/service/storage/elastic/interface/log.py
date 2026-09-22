from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.elastic.driver.factory import storage_manager
from tracardi.config import tracardi

async def save(data) -> BulkInsertResult:
    if tracardi.save_logs:
        return await storage_manager('log').upsert(data)
    return BulkInsertResult(saved=0, errors=[], ids=[])