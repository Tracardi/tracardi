from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.factory import storage_manager
from tracardi.service.storage.index import resources


async def count(query: dict = None):
    return await storage_manager('api-instance').count(query)


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


async def exists():
    es = ElasticClient.instance()
    index = resources.get_index("api-instance")
    index = index.get_write_index()
    return await es.exists_index(index)


async def refresh():
    return await storage_manager('api-instance').refresh()
