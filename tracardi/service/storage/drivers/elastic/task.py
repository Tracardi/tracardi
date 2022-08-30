from tracardi.domain.storage_record import StorageRecords
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.factory import storage_manager
from tracardi.domain.task import Task


async def load_tasks(query, start: int = 0, limit: int = 100) -> StorageRecords:
    query = {
        "from": start,
        "size": limit,
        "query": query,
        "sort": [{"timestamp": {"order": "desc"}}]
    }
    return await storage_manager("task").query(query)


async def upsert_task(task: Task) -> BulkInsertResult:
    return await storage_manager('task').upsert(task.dict(), replace_id=True)


async def delete_task(id: str) -> dict:
    return await storage_manager("task").delete(id)


async def refresh():
    return await storage_manager("task").refresh()
