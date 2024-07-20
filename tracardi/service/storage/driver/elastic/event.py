from datetime import datetime

from tracardi.service.storage.elastic.driver.agg_result import AggResult
from tracardi.domain.event import Event
from tracardi.domain.named_entity import NamedEntity

from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.domain.storage_record import StorageRecords, StorageRecord
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.elastic.driver.elastic_storage import ElasticFiledSort
from tracardi.service.storage.elastic.driver.factory import storage_manager, StorageForBulk
from typing import List, Optional, Dict, Tuple, Union, Set
from tracardi.service.storage.elastic.interface import raw as raw_db

from ...mysql.service.event_source_service import EventSourceService

logger = get_logger(__name__)


async def load(id: str) -> Optional[StorageRecord]:
    return await storage_manager("event").load(id)


async def save(events: Union[List[Event], Set[Event]], exclude=None):
    return await storage_manager("event").upsert(events, exclude=exclude)


async def delete_by_id(id: str) -> dict:
    sm = storage_manager("event")
    # Delete in all indices
    return await sm.delete(id, index=sm.get_multi_storage_alias())


async def unique_field_value(query, limit) -> AggResult:
    return await StorageForBulk().index('event').uniq_field_value("type", search=query, limit=limit)


def _get_name(source_names_idx, id):
    return source_names_idx[id] if id in source_names_idx else id


async def search(query: dict):
    return await storage_manager("event").query({"query": query})


async def query(query: dict) -> StorageRecords:
    return await storage_manager("event").query(query)


async def count_events_by_type(profile_id: str, event_type: str, time_span: int) -> int:
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


async def aggregate_event_by_field_within_time(profile_id,
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
        output = { item['key']: item['doc_count'] for item in buckets}
    else:
        buckets = result.aggregations('events_bucket')
        output = {
            mapping.get(metric, metric): buckets['value']
        }

    return {
        "result": output,
        "total": result.total
    }


async def load_event_by_type(event_type, limit=1) -> StorageRecords:
    return await storage_manager('event').load_by('type', event_type, limit=limit)


async def load_event_by_values(key_value_pairs: List[tuple], sort_by: Optional[List[ElasticFiledSort]] = None,
                               limit: int = 20) -> StorageRecords:
    return await raw_db.load_by_key_value_pairs('event', key_value_pairs, sort_by, limit=limit)


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

    ess =  EventSourceService()
    event_source_as_named_entities = (await ess.load_all_in_deployment_mode()).as_named_entities()

    source_names_idx = {source.id: source.name for source in event_source_as_named_entities}
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


async def get_nth_last_event(event_type: str, n: int, profile_id: Optional[str] = None):
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


async def get_events_by_session(session_id: str, limit: int = 100) -> StorageRecords:
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


async def get_events_by_profile(profile_id: str, limit: int = 100) -> StorageRecords:

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


async def count(query: dict = None):
    return await storage_manager('event').count(query)


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


async def get_events_by_session_and_profile(profile_id: str, session_id: str, limit: int = 100) -> StorageRecords:
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


def scan(query: dict = None, batch: int = 1000):
    return storage_manager('event').scan(query, batch)


async def reassign_session(new_session_id: str, old_session_id: str, profile_id: str):
    result = await get_events_by_session_and_profile(profile_id, old_session_id)
    for event_record in result:
        try:
            event_record['_id'] = event_record['id']
            event_record['session']['id'] = new_session_id
            await storage_manager('event').upsert(event_record)
        except Exception as e:
            logger.error(str(e))


async def get_all_events_by_fields(
        search_by: List[Tuple[str, str]],
        return_fields: Optional[List[str]] = None,
        date_from: Union[str, datetime] = None,
        date_to: Union[str, datetime] = 'now',
) -> List[StorageRecords]:
    def get_query(chunk=0, size=500):
        query = {
            "sort": [
                {"metadata.time.insert": {"order": "asc"}}
            ],
            "from": chunk * size,
            "size": size,
            "query": {
                "bool": {
                    "must": []
                }
            }
        }

        if date_from and date_to:
            query['query']['bool']['must'].append({
                "range": {
                    "metadata.time.insert": {
                        "gte": date_from,
                        "lte": date_to
                    }
                }
            })
        elif date_to:
            query['query']['bool']['must'].append({
                "range": {
                    "metadata.time.insert": {
                        "lte": date_to
                    }
                }
            })

        if return_fields:
            query['_source'] = return_fields

        for field, value in search_by:
            query['query']['bool']['must'].append({
                "term": {field: value}
            })

        return query

    chunk = 0
    while True:
        query = get_query(chunk, size=500)
        chunk += 1
        result = await storage_manager('event').query(query)

        if not bool(result):
            break
        yield result
