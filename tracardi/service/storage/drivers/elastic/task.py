from tracardi.service.storage.factory import storage_manager
from tracardi.domain.task import Task


async def load_tasks(limit: int = 100):
    return list(await storage_manager("task").load_all(limit=limit, sort=[{"timestamp": {"order": "desc"}}]))


async def upsert_task(task: Task):
    return await storage_manager('task').upsert(task.dict(), replace_id=True)


async def delete_task(id: str):
    return await storage_manager("task").delete(id)


async def get_progress(task_id: str):
    result = await storage_manager('task').load(task_id)
    if result is None:
        return None
    return result["progress"]
