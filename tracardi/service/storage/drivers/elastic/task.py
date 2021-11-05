import time

from tracardi.service.storage.factory import storage_manager, StorageForBulk


async def load_pending_tasks(limit: int = 100):
    now = time.time()
    query = {
        "size": limit,
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "timestamp": {
                                "lte": now
                            }
                        }
                    },
                    {
                        "term": {
                            "status": {
                                "value": "pending"
                            }
                        }
                    }
                ]
            }
        }
    }
    return await storage_manager('task').filter(query)


async def save_tasks(tasks):
    return await StorageForBulk(tasks).index('task').save()


async def load_all(start: int = 0, limit: int = 100):
    return await storage_manager('task').load_all(start, limit)

async def create(data: list):
    return await storage_manager('task').upsert(data=data, replace_id=True)
