from datetime import datetime, timedelta
from typing import Optional

from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.elastic.driver.factory import storage_manager
from tracardi.service.utils.date import now_in_utc


# from tracardi.service.storage.elastic_client import ElasticClient
# from tracardi.service.storage.index import Resource


async def save(data) -> BulkInsertResult:
    return await storage_manager('log').upsert(data)


# async def load_all(start: int = 0, limit: int = 100) -> dict:
#     result = await storage_manager('log').load_all(
#         start,
#         limit,
#         sort=[{"date": {"order": "desc", "format": "strict_date_optional_time_nanos"}}])
#     return result.dict()


async def group_by_level(date_from: Optional[datetime] = None) -> dict:
    if date_from is None:
        date_from = now_in_utc() - timedelta(days=30)

    query = {
        "size": 0,
        "query": {
            "range": {
                "date": {
                    "gte": date_from,
                    # "format": "yyyy-MM-dd'T'HH:mm:ss"
                }
            }
        },
        "aggs": {
            "error_levels": {
                "terms": {
                    "field": "level",
                    "size": 10
                }
            }
        }
    }

    result = await storage_manager('log').query(query)
    buckets = result.aggregations('error_levels').buckets()
    return {item['key']:item['doc_count'] for item in buckets}


# async def exists():
#     es = ElasticClient.instance()
#     index = Resource().get_index_constant("log")
#     # Check for template as index will be created with first insert. So there may not be an index but everything is ok
#     # because template exists.
#     return await es.exists_index_template(name=index.get_prefixed_template_name())
