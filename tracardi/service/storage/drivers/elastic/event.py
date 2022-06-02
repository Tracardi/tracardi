import logging
from datetime import datetime, timedelta

from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.drivers.elastic.tag import get_tags
from tracardi.service.storage.elastic_storage import ElasticFiledSort
from tracardi.service.storage.factory import StorageFor, storage_manager
from typing import Union, List, Optional, Dict
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.value_object.save_result import SaveResult
from tracardi.service.storage.factory import StorageForBulk
from tracardi.domain.event import Event
from tracardi.config import tracardi

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


def _get_name(source_names_idx, id):
    return source_names_idx[id] if id in source_names_idx else id


async def search(query):
    return await storage_manager("event").query({"query": query})


async def count_events_by_type(profile_id: str, event_type: str, time_span: int) -> int:
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "metadata.time.insert": {
                                "gte": "now-{}s".format(time_span),
                                "lte": "now"}
                        }
                    },
                    {
                        "term": {
                            "type": event_type
                        }
                    },
                    {
                        "term": {
                            "profile.id": profile_id
                        }
                    }
                ]
            }
        }

    }


    result = await storage_manager("event").query(query)
    return result["hits"]["total"]['value']


async def aggregate_event_by_field_within_time(profile_id, field, time_span):
    query = {
        "bool": {
            "must": [
                {
                    "range": {
                        "metadata.time.insert": {
                            "gte": "now-{}s".format(time_span),
                            "lte": "now"}
                    }
                },
                {
                    "term": {
                        "profile.id": profile_id
                    }
                }
            ]
        }
    }

    result = await _aggregate_event("events_bucket", field, filter_query=query)
    return {
        "total": result.total,
        "buckets": result.aggregations['events_bucket'][0]
    }


async def heatmap_by_event_type(event_type=None):
    query = {
        "size": 0,
        "aggs": {
            "items_over_time": {
                "date_histogram": {
                    "min_doc_count": 1,
                    "field": "metadata.time.insert",
                    "fixed_interval": "1d",
                    "extended_bounds": {
                        "min": datetime.utcnow() - timedelta(days=1 * 365),
                        "max": datetime.utcnow()
                    }
                }
            }
        }
    }

    if event_type is not None:
        query["query"] = {"term": {"type": event_type}}

    result = await storage_manager(index="event").query(query)
    return result['aggregations']["items_over_time"]['buckets']


async def heatmap_by_profile(profile_id=None, bucket_name="items_over_time") -> StorageAggregateResult:
    query = {
        "size": 0,
        "aggs": {
            bucket_name: {
                "date_histogram": {
                    "min_doc_count": 1,
                    "field": "metadata.time.insert",
                    "fixed_interval": "1d",
                    "extended_bounds": {
                        "min": datetime.utcnow() - timedelta(days=1 * 365),
                        "max": datetime.utcnow()
                    }
                }
            }
        }
    }

    if profile_id is not None:
        query["query"] = {"term": {"profile.id": profile_id}}

    return await storage_manager(index="event").aggregate(query, aggregate_key='key_as_string')


async def save_events(events: List[Event], persist_events: bool = True) -> Union[SaveResult, BulkInsertResult]:
    if persist_events:
        events_to_save = []
        for event in events:
            if event.is_persistent():
                try:
                    event.tags.values = (tag.lower() for tag in
                                         set(event.tags.values + tuple(await get_tags(event.type))))
                except ValueError as e:
                    logger.error(str(e))
                finally:
                    events_to_save.append(event)

        event_result = await StorageForBulk(events_to_save).index('event').save(exclude={"update": ...})
        event_result = SaveResult(**event_result.dict())

        # Add event types
        for event in events:
            event_result.types.append(event.type)
    else:
        event_result = BulkInsertResult()

    return event_result


async def load_event_by_type(event_type, limit=1):
    return await StorageFor.crud('event', class_type=Event).load_by('type', event_type, limit=limit)


async def load_event_by_profile(profile_id: str, limit: int = 20) -> List[Event]:
    return await StorageFor.crud('event', class_type=Event).load_by('profile.id', profile_id, limit=limit)


async def load_event_by_values(key_value_pairs: List[tuple], sort_by: Optional[List[ElasticFiledSort]] = None,
                               limit: int = 20) -> List[Event]:
    return await StorageFor.crud('event', class_type=Event).load_by_values(key_value_pairs, sort_by, limit=limit)


async def aggregate_profile_events_by_type(profile_id: str, bucket_name) -> StorageAggregateResult:
    aggregate_query = {
        bucket_name: {
            "terms": {
                "field": "type",
                "size": 15,
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


async def _aggregate_event(bucket_name, by, filter_query=None, buckets_size=15) -> StorageAggregateResult:
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
    result = await _aggregate_event(bucket_name, "type")

    if bucket_name not in result.aggregations:
        return []

    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def aggregate_event_tag() -> List[Dict[str, str]]:
    bucket_name = "by_tag"
    result = await _aggregate_event(bucket_name, "tags.values")

    if bucket_name not in result.aggregations:
        return []

    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def aggregate_event_status() -> List[Dict[str, str]]:
    bucket_name = "by_status"
    result = await _aggregate_event(bucket_name, "metadata.status")

    if bucket_name not in result.aggregations:
        return []

    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def aggregate_events_by_source():
    result = await _aggregate_event(bucket_name='by_source', by="source.id")

    if 'by_source' not in result.aggregations:
        return []

    query_string = [f"id:{id}" for id in result.aggregations['by_source'][0]]
    query_string = " OR ".join(query_string)
    sources = await storage_manager('event-source').load_by_query_string(query_string)
    source_names_idx = {source['id']: source['name'] for source in sources}
    return [{"name": _get_name(source_names_idx, id), "value": count} for id, count in
            result.aggregations['by_source'][0].items()]


async def load_events_heatmap(profile_id: str = None):
    if profile_id is not None:
        filter_query = {
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
    else:
        filter_query = {"match_all": {}}

    # todo add range - one year
    query = {
        "size": 0,
        "query": filter_query,
        "aggs": {
            "by_time": {
                "date_histogram": {
                    # "min_doc_count": 0,
                    "field": "metadata.time.insert",
                    "fixed_interval": "1d",
                    # "extended_bounds": {
                    #     "min": min_date_time,
                    #     "max": max_date_time
                    # }
                },
                "aggs": {
                    "by_source": {
                        "terms": {
                            "field": "type"
                        }
                    }
                }
            }
        },

    }

    raw_result = await storage_manager(index="event").query(query)

    def convert_data(raw_result):
        if 'aggregations' in raw_result:
            for aggregation, data_bucket in raw_result['aggregations'].items():
                if 'buckets' in data_bucket:
                    for row in data_bucket['buckets']:
                        date = row['key_as_string']
                        record = {
                            "date": date,
                            "total": row['doc_count'],
                            "details": []
                        }

                        if 'by_source' in row:
                            by_source = row['by_source']
                            if 'buckets' in by_source:
                                for detail in by_source['buckets']:
                                    record['details'].append(
                                        {
                                            "name": detail['key'],
                                            "date": date,
                                            "value": detail['doc_count']
                                        }
                                    )
                        yield record

    return list(convert_data(raw_result))


async def update_tags(event_type: str, tags: List[str]):
    tags = [tag.lower() for tag in tags]
    query = {
        "script": {
            "source": f"ctx._source.tags.values = {tags}; ctx._source.tags.count = {len(tags)}",
            "lang": "painless"
        },
        "query": {
            "bool": {
                "must": {"match": {"type": event_type}},
                "must_not": {
                    "bool": {
                        "must": [
                            *[{"term": {"tags.values": tag}} for tag in tags],
                            {"term": {"tags.count": len(tags)}}
                        ]
                    }
                }
            }
        }
    }
    return await storage_manager(index="event").update_by_query(query=query)


async def aggregate_timespan_events(time_from: datetime, time_to: datetime,
                                    aggregate_query: dict) -> StorageAggregateResult:
    query = {
        "size": 0,
        "query": {
            "bool": {
                "must": {
                    "range": {
                        "metadata.time.insert": {
                            "gte": time_from,
                            "lte": time_to
                        }
                    }
                }
            }
        },
        "aggs": aggregate_query
    }
    return await storage_manager(index="event").aggregate(query)


async def refresh():
    return await storage_manager('event').refresh()


async def flush():
    return await storage_manager('event').flush()


async def get_nth_last_event(event_type: str, n: int, profile_id: str = None):
    profile_term = {"profile.id": profile_id} if profile_id is not None else {"metadata.profile_less": True}

    result = (await storage_manager("event").query({
        "query": {
            "bool": {
                "must": [
                    {"term": {"type": event_type}},
                    {"term": profile_term}
                ]
            }
        },
        "size": 11,
        "sort": [
            {"metadata.time.insert": "desc"}
        ]
    }))["hits"]["hits"]

    return result[n]["_source"] if len(result) >= n + 1 else None


async def get_event_data_for_session(session_id: str, limit: int = 20):
    result = await storage_manager("event").query({
        "query": {
            "term": {
                "session.id": session_id
            }
        },
        "size": limit,
        "sort": [
            {
                "metadata.time.insert": {"order": "desc"}
            }
        ]
    })
    return [{
        "id": doc["_source"]["id"],
        "insert": doc["_source"]["metadata"]["time"]["insert"],
        "status": doc["_source"]["metadata"]["status"],
        "type": doc["_source"]["type"]
    } for doc in result["hits"]["hits"]], result["hits"]["total"]["value"] > len(result["hits"]["hits"])


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
                result["aggregations"]["by_type"]["buckets"]]
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
        return [{"name": bucket["key"], "value": bucket["doc_count"]} for bucket in
                result["aggregations"]["by_tag"]["buckets"]]
    except KeyError:
        return []


async def count(query: dict = None):
    return await storage_manager('event').count(query)


async def get_avg_process_time():
    result = await storage_manager("event").query({
        "size": 0,
        "aggs": {
            "avg_process_time": {"avg": {"field": "metadata.time.process_time"}}
        }
    })

    try:
        return {
            "avg": result['aggregations']['avg_process_time']['value'],
            "records": result['hits']['total']['value']
        }
    except KeyError:
        return {
            "avg": 0,
            "records": 0
        }
