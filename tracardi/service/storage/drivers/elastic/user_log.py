from tracardi.service.storage.factory import storage_manager
from datetime import datetime


async def add_log(successful: bool, email: str):
    return await storage_manager("user-logs").upsert({
        "timestamp": datetime.utcnow(),
        "email": email,
        "successful": successful
    })


async def load_logs(start: int = 0, limit: int = 100):
    return await storage_manager("user-logs").load_all(start, limit)


async def load_within_period(upper: int, lower: int, start: int = 0, limit: int = 100):
    return await storage_manager("user-logs").query({
        "query": {
            "range": {
                "timestamp": {
                    "gte": datetime.fromtimestamp(lower),
                    "lte": datetime.fromtimestamp(upper)
                }
            }
        },
        "from": start,
        "size": limit,
        "sort": [
            {"timestamp": "desc"}
        ]
    })
