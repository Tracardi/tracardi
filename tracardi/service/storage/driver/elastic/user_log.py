from tracardi.service.storage.factory import storage_manager
from datetime import datetime


async def load_logs(start: int = 0, limit: int = 100, query_string: str = None):
    query = {
        "query": {
            "query_string": {
                "query": query_string
            }
        } if query_string is not None else {"match_all": {}},
        "from": start,
        "size": limit,
        "sort": [
            {"timestamp": "desc"}
        ]
    }
    return await storage_manager("user-logs").query(query)


async def add_log(email: str, successful: bool):
    return await storage_manager("user-logs").upsert(
        {
            "email": email,
            "successful": successful,
            "timestamp": datetime.utcnow()
        }
    )
