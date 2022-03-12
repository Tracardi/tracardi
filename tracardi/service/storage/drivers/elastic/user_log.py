from tracardi.service.storage.factory import storage_manager
from datetime import datetime


async def load_logs(start: int = 0, limit: int = 100, email: str = None, lower: int = None, upper: int = None):
    query = {
        "query": {
            "wildcard": {
                "email": f"{email if email is not None else ''}*"
            }
        },
        "from": start,
        "size": limit,
        "sort": [
            {"timestamp": "desc"}
        ]
    }

    if lower is not None and upper is not None:
        query["query"]["range"] = {
            "timestamp": {
                "gte": datetime.fromtimestamp(lower),
                "lte": datetime.fromtimestamp(upper)
            }
        }
    return await storage_manager("user-logs").query(query)
