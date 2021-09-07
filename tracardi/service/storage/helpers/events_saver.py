from typing import Union, List

from tracardi.domain.event import Event

from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.value_object.save_result import SaveResult
from tracardi.service.storage.factory import StorageForBulk


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
