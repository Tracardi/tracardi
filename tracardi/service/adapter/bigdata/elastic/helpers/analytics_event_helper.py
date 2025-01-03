from typing import List, Dict

from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.elastic.driver.factory import storage_manager
from tracardi.service.storage.mysql.interface import event_source_dao


def _get_name(source_names_idx, id):
    return source_names_idx[id] if id in source_names_idx else id


async def _aggregate_event(bucket_name, by, filter_query=None, buckets_size=100) -> StorageAggregateResult:
    aggregate_query = {
        bucket_name: {
            "terms": {
                "field": by,
                "size": buckets_size,
            }
        }
    }

    if filter_query is None:
        filter_query = {
            "match_all": {}
        }

    query = {
        "size": 0,
        "query": filter_query,
        "aggs": aggregate_query
    }

    return await storage_manager(index="event").aggregate(query)


async def aggregate_event_type() -> List[Dict[str, str]]:
    bucket_name = "by_type"

    query = {
        "bool": {
            "must": {
                "range": {
                    "metadata.time.insert": {
                        "gte": "now-1M",
                        "lte": "now"
                    }
                }
            }
        }
    }

    result = await _aggregate_event(bucket_name, "type", query, buckets_size=12)

    if bucket_name not in result.aggregations:
        return []

    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def aggregate_source_by_type(source_id: str, time_span: str):
    result = await storage_manager("event").query({
        "query": {
            "bool": {
                "must": [
                    {"term": {"source.id": source_id}},
                    {"range": {"metadata.time.insert": {"gte": f"now-1{time_span}"}}}
                ]
            }
        },
        "size": 0,
        "aggs": {
            "by_type": {
                "terms": {
                    "field": "type"
                }
            }
        }
    })

    try:
        return [{"name": bucket["key"], "value": bucket["doc_count"]} for bucket in
                result.aggregations("by_type").buckets()]
    except KeyError:
        return []


async def aggregate_source_by_tags(source_id: str, time_span: str):
    result = await storage_manager("event").query({
        "query": {
            "bool": {
                "must": [
                    {"term": {"source.id": source_id}},
                    {"range": {"metadata.time.insert": {"gte": f"now-1{time_span}"}}}
                ]
            }
        },
        "size": 0,
        "aggs": {
            "by_tag": {
                "terms": {"field": "tags.values"}
            }
        }
    })

    try:
        return [
            {"name": bucket["key"], "value": bucket["doc_count"]} for bucket in
            result.aggregations("by_tag").buckets()
        ]
    except KeyError:
        return []


async def aggregate_event_tag() -> List[Dict[str, str]]:
    bucket_name = "by_tag"

    query = {
        "bool": {
            "must": {
                "range": {
                    "metadata.time.insert": {
                        "gte": "now-1M",
                        "lte": "now"
                    }
                }
            }
        }
    }

    result = await _aggregate_event(bucket_name, "tags.values", filter_query=query, buckets_size=20)

    if bucket_name not in result.aggregations:
        return []

    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def get_avg_process_time():
    result = await storage_manager("event").query({
        "size": 0,
        "aggs": {
            "avg_process_time": {"avg": {"field": "metadata.time.total_time"}}
        }
    })

    try:
        return {
            "avg": result.aggregations('avg_process_time')['value'],
            "records": result.total
        }
    except KeyError:
        return {
            "avg": 0,
            "records": 0
        }


async def aggregate_event_status() -> List[Dict[str, str]]:
    bucket_name = "by_status"

    query = {
        "bool": {
            "must": {
                "range": {
                    "metadata.time.insert": {
                        "gte": "now-1M",
                        "lte": "now"
                    }
                }
            }
        }
    }

    result = await _aggregate_event(bucket_name, "metadata.status", filter_query=query, buckets_size=20)

    if bucket_name not in result.aggregations:
        return []

    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def aggregate_event_device_geo() -> List[Dict[str, str]]:
    bucket_name = "by_device_geo"

    query = {
        "bool": {
            "must": {
                "range": {
                    "metadata.time.insert": {
                        "gte": "now-1M",
                        "lte": "now"
                    }
                }
            }
        }
    }

    result = await _aggregate_event(bucket_name, "device.geo.country.name", filter_query=query, buckets_size=15)

    if bucket_name not in result.aggregations:
        return []

    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def aggregate_event_os_name() -> List[Dict[str, str]]:
    bucket_name = "by_os_name"

    query = {
        "bool": {
            "must": {
                "range": {
                    "metadata.time.insert": {
                        "gte": "now-1M",
                        "lte": "now"
                    }
                }
            }
        }
    }

    result = await _aggregate_event(bucket_name, "os.name", filter_query=query, buckets_size=20)

    if bucket_name not in result.aggregations:
        return []

    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def aggregate_event_channels() -> List[Dict[str, str]]:
    bucket_name = "by_channel"

    query = {
        "bool": {
            "must": {
                "range": {
                    "metadata.time.insert": {
                        "gte": "now-1M",
                        "lte": "now"
                    }
                }
            }
        }
    }

    result = await _aggregate_event(bucket_name, "metadata.channel", filter_query=query, buckets_size=20)

    if bucket_name not in result.aggregations:
        return []

    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def aggregate_event_resolution() -> List[Dict[str, str]]:
    bucket_name = "by_resolution"

    query = {
        "bool": {
            "must": {
                "range": {
                    "metadata.time.insert": {
                        "gte": "now-1M",
                        "lte": "now"
                    }
                }
            }
        }
    }

    result = await _aggregate_event(bucket_name, "device.resolution", filter_query=query, buckets_size=20)

    if bucket_name not in result.aggregations:
        return []

    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def aggregate_events_by_source(buckets_size):
    query = {
        "bool": {
            "must": {
                "range": {
                    "metadata.time.insert": {
                        "gte": "now-1M",
                        "lte": "now"
                    }
                }
            }
        }
    }

    result = await _aggregate_event(bucket_name='by_source', by="source.id", filter_query=query,
                                    buckets_size=buckets_size)

    if 'by_source' not in result.aggregations:
        return []

    query_string = [f"id:{id}" for id in result.aggregations['by_source'][0]]
    query_string = " OR ".join(query_string)

    event_source_as_named_entities, _ = await event_source_dao.load_event_source_entities()

    source_names_idx = {source.id: source.name for source in event_source_as_named_entities}
    return [{"name": _get_name(source_names_idx, id), "value": count} for id, count in
            result.aggregations['by_source'][0].items()]


async def load_events_avg_requests():
    result = await storage_manager(index="event").count(query={
        "query": {
            "range": {
                "metadata.time.insert": {
                    "gte": "now-5m",
                    "lte": "now"
                }
            }
        }
    })
    return result['count'] / (5 * 60) if 'count' in result else 0


async def aggregate_events_by_type_and_source() -> StorageRecords:
    return await storage_manager("event").query({
        "query": {
            "match_all": {}
        },
        "size": 0,
        "aggs": {
            "by_type": {
                "terms": {
                    "field": "type",
                    "size": 100,
                    "order": {
                        "_key": "asc"
                    }
                },
                "aggs": {
                    "by_source": {
                        "terms": {
                            "field": "source.id",
                            "size": 20
                        },
                        # "aggs": {
                        #     "last": {
                        #         "top_hits": {
                        #             "size": 1
                        #         }
                        #     }
                        # }
                    }
                }
            }
        }
    })
