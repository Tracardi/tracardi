from typing import Optional, List, Dict, Union, Set

from tracardi.domain.event import Event
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.domain.storage_record import StorageRecord, StorageRecords
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.elastic.driver.agg_result import AggResult
from tracardi.service.storage.elastic.driver.factory import storage_manager, StorageForBulk
from tracardi.service.storage.mysql.interface import event_source_dao
from tracardi.service.storage.elastic.dal import raw as raw_db


async def refresh():
    return await raw_db.refresh('event')


async def flush():
    return await raw_db.flush('event')


async def count(query: dict = None):
    return await raw_db.count('event', query)


async def _save_events(events: Union[List[Event], Set[Event]], exclude=None):
    return await storage_manager('event').upsert(events, exclude=exclude)


async def _delete_by_id(id: str) -> dict:
    sm = storage_manager('event')
    # Delete in all indices
    return await sm.delete(id, index=sm.get_multi_storage_alias())


async def _load(id: str) -> Optional[StorageRecord]:
    return await storage_manager("event").load(id)


async def _get_nth_last_event(event_type: str, n: int, profile_id: Optional[str] = None):
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
    }))

    return result[n] if len(result) >= n + 1 else None


async def _unique_field_value(query, limit) -> AggResult:
    return await StorageForBulk().index('event').uniq_field_value("type", search=query, limit=limit)


async def _get_events_by_session_and_profile(profile_id: str, session_id: str, limit: int = 100) -> StorageRecords:
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"profile.id": profile_id}},
                    {"term": {"session.id": session_id}}
                ]
            }
        },
        "sort": [
            {
                "metadata.time.insert": {"order": "desc"}
            }
        ],
        "size": limit
    }
    return await storage_manager("event").query(query)


async def _get_events_by_profile(profile_id: str, limit: int = 100) -> StorageRecords:
    query = {
        "query": {
            "term": {
                "profile.id": profile_id
            }
        },
        "size": limit,
        "sort": [
            {
                "metadata.time.insert": {"order": "desc"}
            }
        ]
    }

    return await storage_manager("event").query(query)


async def _get_events_by_session(session_id: str, limit: int = 100) -> StorageRecords:
    query = {
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
    }
    return await storage_manager("event").query(query)


async def _aggregate_profile_events(profile_id: str, aggregate_query: dict) -> StorageAggregateResult:
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


async def _aggregate_profile_events_by_field(profile_id: str, field: str, bucket_name: str,
                                             size: int = 15) -> StorageAggregateResult:
    aggregate_query = {
        bucket_name: {
            "terms": {
                "field": field,
                "size": size,
            }
        }
    }

    return await _aggregate_profile_events(profile_id, aggregate_query)


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


async def _aggregate_event_type() -> List[Dict[str, str]]:
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


async def _aggregate_source_by_type(source_id: str, time_span: str) -> List[dict]:
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


async def _aggregate_source_by_tags(source_id: str, time_span: str) -> List[dict]:
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


async def _aggregate_event_tag() -> List[Dict[str, str]]:
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


async def _get_avg_process_time() -> dict:
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


async def _aggregate_event_status() -> List[Dict[str, str]]:
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


async def _aggregate_event_device_geo() -> List[Dict[str, str]]:
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


async def _aggregate_event_os_name() -> List[Dict[str, str]]:
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


async def _aggregate_event_channels() -> List[Dict[str, str]]:
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


async def _aggregate_event_resolution() -> List[Dict[str, str]]:
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


def _get_name(source_names_idx, id):
    return source_names_idx[id] if id in source_names_idx else id


async def _aggregate_events_by_source(buckets_size) -> List[dict]:
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


async def _aggregate_events_by_type_and_source() -> StorageRecords:
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


async def _aggregate_event_by_field_within_time(profile_id,
                                                field,
                                                time_span,
                                                metric='term',
                                                event_type: NamedEntity = NamedEntity(id='', name='')):
    mapping = {
        "terms": "counts"
    }

    query = {
        # "size": 0,
        "query": {
            "bool": {
                "filter": [
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
        },
        "aggs": {
            "events_bucket": {
                metric: {
                    "field": field
                }
            }
        }
    }

    if metric == 'terms':
        query['aggs']['events_bucket']['terms']['size'] = 100

    if not event_type.is_empty():
        query['query']['bool']['filter'].append({
            "term": {
                "type": event_type.id
            }
        })

    result = await storage_manager(index="event").query(query)
    if metric == 'terms':
        buckets = result.aggregations('events_bucket').buckets()
        output = {item['key']: item['doc_count'] for item in buckets}
    else:
        buckets = result.aggregations('events_bucket')
        output = {
            mapping.get(metric, metric): buckets['value']
        }

    return {
        "result": output,
        "total": result.total
    }


async def _count_events_by_type(profile_id: str, event_type: str, time_span: int) -> int:
    # todo rewrite to use count instead of query
    query = {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
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

    return result.total


async def _count_events_in_db(query: dict = None):
    return await raw_db.count('event', query)


async def load_nth_last_event(event_type: str, offset: int, profile_id: Optional[str] = None):
    return await _get_nth_last_event(
        profile_id=profile_id,
        event_type=event_type,
        n=(-1) * offset
    )


async def load_events_by_profile_id(profile_id: str, limit: int) -> dict:
    result = await _get_events_by_profile(
        profile_id,
        limit)
    return result.dict()


async def load_events_by_session(session_id: str, limit: int) -> Optional[List[Event]]:
    result = await _get_events_by_session(session_id, limit)

    if result.total == 0:
        return None

    return result.to_domain_objects(Event)


async def aggregate_profile_events_from_db(profile_id, aggregate_query):
    return await _aggregate_profile_events(
        profile_id=profile_id,
        aggregate_query=aggregate_query
    )


async def aggregate_events_by_profile_and_field(profile_id: str, field: str, bucket_name: str):
    return await _aggregate_profile_events_by_field(profile_id,
                                                    field=field,
                                                    bucket_name=bucket_name)


async def aggregate_event_by_field_within_time(profile_id: str, field_id: str, span_in_sec: int, metric, event_type):
    return await _aggregate_event_by_field_within_time(
        profile_id,
        field_id,
        span_in_sec,
        metric,
        event_type
    )


async def count_events_by_type(profile_id: str, event_type_id: str, span_in_sec: int):
    return await _count_events_by_type(
        profile_id,
        event_type_id,
        span_in_sec
    )


def scan(query: dict = None, batch: int = 1000):
    return storage_manager('event').scan(query, batch)


async def update_profile_event(old_id: str, merged_profile_id):
    await raw_db.update_profile_ids('event', old_id, merged_profile_id)
