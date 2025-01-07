from typing import Optional

from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.elastic.driver.factory import storage_manager


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


async def load_active_profile_by_field(field: str, value: str, start: int = 0, limit: int = 100) -> StorageRecords:
    query = {
        "from": start,
        "size": limit,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            field: value
                        }
                    },
                    {
                        "term": {
                            "active": True
                        }
                    }
                ]
            }
        }
    }
    return await storage_manager('profile').query(query)

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