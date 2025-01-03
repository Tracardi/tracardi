from typing import List

from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.service.storage.elastic.driver.factory import storage_manager


async def _aggregate_events_by_profile_and_field(profile_id: str, field: str, bucket_name: str):
    return await aggregate_profile_events_by_field(profile_id,
                                                            field=field,
                                                            bucket_name=bucket_name)

async def load_events_by_profile_and_field(profile_id: str, field: str, table: bool = False):
    bucket_name = f"by_{field}"
    result = await _aggregate_events_by_profile_and_field(profile_id,
                                                         field=field,
                                                         bucket_name=bucket_name)
    if table:
        return {id: count for id, count in result.aggregations[bucket_name][0].items()}
    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def count_profile_duplicates(profile_ids: List[str]):
    return await storage_manager('profile').count({
        "query": {
            "bool": {
                "should": [
                    {
                        "terms": {
                            "ids": profile_ids
                        }
                    },
                    {
                        "terms": {
                            "id": profile_ids
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
    })

async def load_modified_top_profiles(size):
    query = {
        "size": size,
        "sort": [
            {
                "metadata.time.update": {
                    "order": "desc"
                }
            }
        ]
    }
    return await storage_manager('profile').query(query)


async def aggregate_profile_events_by_type(profile_id: str, bucket_name) -> StorageAggregateResult:
    return await aggregate_profile_events_by_field(profile_id, field="name", bucket_name=bucket_name)


async def aggregate_profile_events_by_field(profile_id: str, field: str, bucket_name: str,
                                            size: int = 15) -> StorageAggregateResult:
    aggregate_query = {
        bucket_name: {
            "terms": {
                "field": field,
                "size": size,
            }
        }
    }

    return await aggregate_profile_events(profile_id, aggregate_query)


async def aggregate_profile_events(profile_id: str, aggregate_query: dict) -> StorageAggregateResult:
    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "profile.id": profile_id
                        }
                    }
                ]
            }
        },
        "aggs": aggregate_query
    }
    return await storage_manager(index="event").aggregate(query)

