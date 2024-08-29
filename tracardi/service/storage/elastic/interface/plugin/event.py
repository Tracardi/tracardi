from typing import List, Optional

from tracardi.service.storage.elastic.dal.event import _aggregate_event_by_field_within_time, _count_events_by_type, \
    _get_nth_last_event
from tracardi.service.storage.elastic.dal.event_fetcher import EventContextFetcher


async def aggregate_event_by_field_within_time(profile_id: str, field_id: str, span_in_sec: int, metric,
                                               event_type) -> dict:
    return await _aggregate_event_by_field_within_time(
        profile_id,
        field_id,
        span_in_sec,
        metric,
        event_type
    )


async def count_events_by_type(profile_id: str, event_type_id: str, span_in_sec: int) -> int:
    return await _count_events_by_type(
        profile_id,
        event_type_id,
        span_in_sec
    )


async def _load_event_types(event_context: EventContextFetcher, query, min_date_range) -> List[str]:
    _event_types = await event_context.fetch_event_types(query, min_date_time=min_date_range)
    return [event['type'] for event in _event_types]


async def load_event_types(profile_id: str, session_id: Optional[str], in_one_session: bool, query, min_date_range):
    if in_one_session:

        if session_id is None:
            raise ValueError("Can not find events in context of session when there is no session in event. "
                             "Is this a profile less or events less event?")

        event_context = EventContextFetcher(profile_id=profile_id,
                                            session_id=session_id)
    else:
        event_context = EventContextFetcher(profile_id=profile_id)

    return await _load_event_types(event_context, query, min_date_range)


async def load_nth_last_event(event_type: str, offset: int, profile_id: Optional[str] = None):
    # TODO to be reviewed. It returns optional dict but the dict may have structure of event
    return await _get_nth_last_event(
        profile_id=profile_id,
        event_type=event_type,
        n=(-1) * offset
    )
