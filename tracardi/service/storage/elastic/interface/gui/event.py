from typing import List, Dict, Optional

from tracardi.domain.event import Event
from tracardi.service.storage.elastic.dal.event import _aggregate_events_by_type_and_source, _refresh, _flush, \
    _get_avg_process_time, _aggregate_event_type, _aggregate_event_tag, _aggregate_event_status, \
    _aggregate_event_device_geo, _aggregate_event_os_name, _aggregate_event_channels, _aggregate_event_resolution, \
    _aggregate_events_by_source, _aggregate_source_by_type, _aggregate_source_by_tags, \
    _get_events_by_session_and_profile, _get_events_by_profile, _load, _delete_by_id
from tracardi.service.storage.elastic.dal import raw as raw_db


def _get_data(result):
    for by_type in result.aggregations('by_type').buckets():
        row = {'type': by_type['key'], 'source': []}
        for bucket in by_type['by_source']['buckets']:
            row['source'].append({
                "id": bucket['key'],
                "count": bucket['doc_count']
            })
        yield row


async def aggregate_events_by_type_and_source() -> List[dict]:
    result = await _aggregate_events_by_type_and_source()
    return list(_get_data(result))


async def refresh_event_db():
    return await _refresh()


async def flush_event_db():
    await _flush()


async def count_events_in_db(query: dict = None):
    return await raw_db.count('event', query)


async def load_events_avg_requests() -> float:
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


async def load_event_avg_process_time() -> dict:
    return await _get_avg_process_time()


async def load_events_by_session_and_profile(profile_id: str, session_id: str, limit: int) -> dict:
    result = await _get_events_by_session_and_profile(
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


async def load_event_from_db(event_id: str) -> Optional[Event]:
    event_record = await _load(event_id)

    if event_record is None:
        return None
    return event_record.to_entity(Event)


async def load_events_by_profile_id(profile_id: str, limit: int) -> dict:
    result = await _get_events_by_profile(
        profile_id,
        limit)
    return result.dict()


async def aggregate_events_by_source_and_type(source_id, time_span) -> List[dict]:
    return await _aggregate_source_by_type(source_id, time_span)


async def aggregate_event_types_from_db() -> List[Dict[str, str]]:
    return await _aggregate_event_type()


async def aggregate_event_tags_from_db() -> List[Dict[str, str]]:
    return await _aggregate_event_tag()


async def aggregate_event_statuses_from_db() -> List[Dict[str, str]]:
    return await _aggregate_event_status()


async def aggregate_event_devices_geo_from_db() -> List[Dict[str, str]]:
    return await _aggregate_event_device_geo()


async def aggregate_event_os_names_from_db() -> List[Dict[str, str]]:
    return await _aggregate_event_os_name()


async def aggregate_event_channels_from_db() -> List[Dict[str, str]]:
    return await _aggregate_event_channels()


async def aggregate_event_resolutions_from_db() -> List[Dict[str, str]]:
    return await _aggregate_event_resolution()


async def aggregate_events_by_source_from_db(buckets_size: int) -> List[dict]:
    return await _aggregate_events_by_source(buckets_size=buckets_size)


async def aggregate_events_by_source_and_tags(source_id, time_span) -> List[dict]:
    return await _aggregate_source_by_tags(source_id, time_span)


async def delete_event_from_db(event_id:str):
    return await _delete_by_id(event_id)