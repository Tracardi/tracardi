from typing import Union, List, Set

from tracardi.domain.event import Event
from tracardi.service.storage.elastic.driver.factory import storage_manager


async def save_events(events: Union[List[Event], Set[Event]], exclude=None):
    return await storage_manager("event").upsert(events, exclude=exclude)


async def save_events_in_db(events):
    return await save_events(events, exclude={"operation": ...})