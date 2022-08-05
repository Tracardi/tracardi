from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.factory import storage_manager
from tracardi.domain.storage_result import StorageResult
from tracardi.service.storage.index import resources


async def load_all(start: int = 0, limit: int = 100) -> StorageResult:
    return await storage_manager('log').load_all(
        start,
        limit,
        sort=[{"date": {"order": "desc", "format": "strict_date_optional_time_nanos"}}])


async def load_by_query_string(query_string: str, start: int = 0, limit: int = 100) -> StorageResult:
    result = await storage_manager('log').query({
        "query": {
            "query_string": {
                "query": query_string
            }
        },
        "sort": [
            {"date": {"order": "desc", "format": "strict_date_optional_time_nanos"}}
        ],
        "from": start,
        "size": limit
    })
    return StorageResult(result)


async def exists():
    es = ElasticClient.instance()
    index = resources.get_index("log")
    # Check for template as index will be created with first insert. So there may not be index but everything is ok
    # because template exists.
    return await es.exists_index_template(name=index.get_prefixed_template_name())
