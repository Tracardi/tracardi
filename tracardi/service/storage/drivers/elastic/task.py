from tracardi.domain.storage_result import StorageResult
from tracardi.service.storage.factory import storage_manager
from tracardi.domain.task import Task


async def load_tasks(query, start: int = 0, limit: int = 100) -> StorageResult:
    query = {
        "from": start,
        "size": limit,
        "query": query,
        "sort": [{"timestamp": {"order": "desc"}}]
    }
    result = await storage_manager("task").query(query)
    return StorageResult(result)


async def upsert_task(task: Task):
    return await storage_manager('task').upsert(task.dict(), replace_id=True)


async def delete_task(id: str):
    return await storage_manager("task").delete(id)
