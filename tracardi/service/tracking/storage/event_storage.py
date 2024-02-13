from typing import List, Union, Set, Optional

from tracardi.context import get_context, Context
from tracardi.domain.event import Event
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.storage.driver.elastic import event as event_db


async def save_events(events: Union[List[Event], Set[Event]], context: Optional[Context] = None) -> BulkInsertResult:

    if context is None:
        context = get_context()

    return await event_db.save(events, exclude={"operation": ...})
