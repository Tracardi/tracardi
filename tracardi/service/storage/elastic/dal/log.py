from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
# from tracardi.service.storage.elastic_client import ElasticClient
from tracardi.service.storage.elastic.driver.factory import storage_manager
# from tracardi.service.storage.index import Resource


async def save(data) -> BulkInsertResult:
    return await storage_manager('log').upsert(data)


# async def load_all(start: int = 0, limit: int = 100) -> dict:
#     result = await storage_manager('log').load_all(
#         start,
#         limit,
#         sort=[{"date": {"order": "desc", "format": "strict_date_optional_time_nanos"}}])
#     return result.dict()


# async def load_by_query_string(query_string: str, start: int = 0, limit: int = 100) -> dict:
#     result = await storage_manager('log').query({
#         "query": {
#             "query_string": {
#                 "query": query_string
#             }
#         },
#         "sort": [
#             {"date": {"order": "desc", "format": "strict_date_optional_time_nanos"}}
#         ],
#         "from": start,
#         "size": limit
#     })
#     return result.dict()


# async def exists():
#     es = ElasticClient.instance()
#     index = Resource().get_index_constant("log")
#     # Check for template as index will be created with first insert. So there may not be an index but everything is ok
#     # because template exists.
#     return await es.exists_index_template(name=index.get_prefixed_template_name())
