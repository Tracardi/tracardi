from typing import Union, List, Set

from tracardi.domain.event import Event
from tracardi.service.storage.elastic.dal import raw as raw_db


async def save_events(events: Union[List[Event], Set[Event]], exclude=None):
    return await raw_db.upsert_document("event", events, exclude=exclude)


async def save_events_in_db(events):
    return await save_events(events, exclude={"operation": ...})