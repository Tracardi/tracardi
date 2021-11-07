import time

from tracardi.service.storage.factory import storage_manager, StorageForBulk
from uuid import uuid4
from datetime import datetime


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


async def create(timestamp, type, properties, context, session_id, source_id, profile_id, status):
    return await storage_manager('task').upsert(data=[{
        "id": uuid4(),
        "timestamp": timestamp,
        "event": {
            "metadata": {
                "time": {
                    "insert": datetime.utcnow()
                }
            },
            "type": type,
            "properties": properties,
            "context": context,
            "session": {
                "id": session_id
            },
            "source": {
                "id": source_id
            },
            "profile": {
                "id": profile_id
            }
        },
        "status": status
    }], replace_id=True)
