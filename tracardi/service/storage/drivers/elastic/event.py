from datetime import datetime, timedelta

from tracardi.domain.storage_aggregate_result import StorageAggregateResult
from tracardi.service.storage.factory import StorageFor, storage_manager
from typing import Union, List

from tracardi.domain.event import Event

from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.value_object.save_result import SaveResult
from tracardi.service.storage.factory import StorageForBulk


async def search(query):
    storage = storage_manager("event")
    return await storage.query({"query": query})


async def count_events_by_type(event_type: str, time_span: int) -> int:
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
                        "match": {
                            "type": event_type
                        }
                    }
                ]
            }
        }

    }
    result = await storage_manager("event").query(query)
    return result["hits"]["total"]


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


async def heatmap_by_profile(profile_id=None):
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

    if profile_id is not None:
        query["query"] = {"term": {"profile.id": profile_id}}

    result = await storage_manager(index="event").query(query)
    return result['aggregations']["items_over_time"]['buckets']


async def save_events(events: List[Event], persist_events: bool = True) -> Union[SaveResult, BulkInsertResult]:
    if persist_events:
        events_to_save = [event for event in events if event.is_persistent()]
        event_result = await StorageForBulk(events_to_save).index('event').save()
        event_result = SaveResult(**event_result.dict())

        # Add event types
        for event in events:
            event_result.types.append(event.type)
    else:
        event_result = BulkInsertResult()

    return event_result


async def load_event_by_type(event_type):
    return await StorageFor.crud('event', class_type=Event).load_by('type', event_type, limit=1)


async def aggregate_profile_events_by_type(profile_id: str) -> StorageAggregateResult:
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
        "aggs": {
            "by_type": {
                "terms": {
                    "field": "type",
                    "size": 15,
                }
            }
        }
    }
    return await storage_manager(index="event").aggregate(query)


async def load_events_heatmap(profile_id: str):
    # todo add range - one year
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
                print(data_bucket)
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
