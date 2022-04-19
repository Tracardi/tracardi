from tracardi.service.storage.factory import storage_manager


async def load_all(start: int = 0, limit: int = 100):
    return await storage_manager('api-instance').load_all(start, limit)


async def remove_dead_instances():
    return await storage_manager('api-instance').delete_by_query({
        "query": {
            "query_string": {
                "query": "timestamp:[* TO now-1d]"
            }
        }
    })
