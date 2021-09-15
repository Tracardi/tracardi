import time

from tracardi.service.storage.factory import storage_manager, StorageForBulk


async def load_tasks():
    now = time.time()
    query = {
        "size": 100,
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
