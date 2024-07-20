from typing import Optional, List, Dict

from tracardi.domain.event import Event
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.driver.elastic import event as event_db


async def refresh_event_db():
    return await event_db.refresh()


async def flush_event_db():
    await event_db.flush()


async def load_event_from_db(event_id: str) -> Optional[Event]:
    event_record = await event_db.load(event_id)

    if event_record is None:
        return None
    return event_record.to_entity(Event)


async def delete_event_from_db(event_id):
    return await event_db.delete_by_id(event_id)


async def count_events_in_db(query: dict = None):
    return await event_db.count(query)


async def load_nth_last_event(event_type: str, offset: int, profile_id: Optional[str] = None):
    return await event_db.get_nth_last_event(
        profile_id=profile_id,
        event_type=event_type,
        n=(-1) * offset
    )


async def load_unique_field_value(search_query, limit):
    return await event_db.unique_field_value(search_query, limit)


async def load_events_avg_requests():
    result = await count_events_in_db(query={
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


async def save_events_in_db(events) -> BulkInsertResult:
    return await event_db.save(events, exclude={"operation": ...})


async def load_events_by_session_and_profile(profile_id: str, session_id: str, limit: int):
    result = await event_db.get_events_by_session_and_profile(
        profile_id,
        session_id,
        limit)

    more_to_load = result.total > len(result)
    result = [{
        "id": doc["id"],
        "metadata": doc["metadata"],
        "type": doc["type"],
        "name": doc.get('name', None),
        "source": doc.get('source'),
        "context": doc.get('context', None)
    } for doc in result]

    return {"result": result, "more_to_load": more_to_load}


async def load_events_by_profile_id(profile_id: str, limit: int) -> dict:
    result = await event_db.get_events_by_profile(
        profile_id,
        limit)
    return result.dict()


async def load_events_by_session(session_id: str, limit: int) -> Optional[List[Event]]:
    result = await event_db.get_events_by_session(session_id, limit)

    if result.total == 0:
        return None

    return result.to_domain_objects(Event)


async def aggregate_profile_events_from_db(profile_id, aggregate_query):
    return await event_db.aggregate_profile_events(
        profile_id=profile_id,
        aggregate_query=aggregate_query
    )


async def aggregate_events_by_profile_and_field(profile_id: str, field: str, bucket_name: str):
    return await event_db.aggregate_profile_events_by_field(profile_id,
                                                            field=field,
                                                            bucket_name=bucket_name)


async def load_events_by_profile_and_field(profile_id: str, field: str, table: bool = False):
    bucket_name = f"by_{field}"
    result = await aggregate_events_by_profile_and_field(profile_id,
                                                         field=field,
                                                         bucket_name=bucket_name)

    if table:
        return {id: count for id, count in result.aggregations[bucket_name][0].items()}
    return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]


async def aggregate_event_types_from_db() -> List[Dict[str, str]]:
    return await event_db.aggregate_event_type()


async def aggregate_events_by_source_and_type(source_id, time_span):
    return await event_db.aggregate_source_by_type(source_id, time_span)


async def aggregate_events_by_source_and_tags(source_id, time_span):
    return await event_db.aggregate_source_by_tags(source_id, time_span)


async def aggregate_event_tags_from_db() -> List[Dict[str, str]]:
    return await event_db.aggregate_event_tag()


async def load_event_avg_process_time():
    return await event_db.get_avg_process_time()


async def aggregate_event_statuses_from_db():
    return await event_db.aggregate_event_status()


async def aggregate_event_devices_geo_from_db():
    return await event_db.aggregate_event_device_geo()


async def aggregate_event_os_names_from_db():
    return await event_db.aggregate_event_os_name()


async def aggregate_event_channels_from_db():
    return await event_db.aggregate_event_channels()


async def aggregate_event_resolutions_from_db():
    return await event_db.aggregate_event_resolution()


async def aggregate_events_by_source_from_db(buckets_size: int):
    return await event_db.aggregate_events_by_source(buckets_size=buckets_size)


async def aggregate_events_by_type_and_source():
    def _get_data(result):
        for by_type in result.aggregations('by_type').buckets():
            row = {'type': by_type['key'], 'source': []}
            for bucket in by_type['by_source']['buckets']:
                row['source'].append({
                    "id": bucket['key'],
                    "count": bucket['doc_count']
                })
            yield row

    result = await event_db.aggregate_events_by_type_and_source()
    return list(_get_data(result))


async def aggregate_event_by_field_within_time(profile_id: str, field_id: str, span_in_sec: int, metric, event_type):
    return await event_db.aggregate_event_by_field_within_time(
        profile_id,
        field_id,
        span_in_sec,
        metric,
        event_type
    )


async def count_events_by_type(profile_id: str, event_type_id: str, span_in_sec: int):
    return await event_db.count_events_by_type(
        profile_id,
        event_type_id,
        span_in_sec
    )
