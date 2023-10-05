from typing import List, Union, Set

from tracardi.domain.event import Event
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.driver.elastic import event as event_db


async def save_events(events: Union[List[Event], Set[Event]]) -> BulkInsertResult:
    return await event_db.save(events, exclude={"operation": ...})
