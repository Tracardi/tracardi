from typing import Tuple, Optional, List

from tracardi.domain.event_redirect import EventRedirect
from tracardi.service.cache.cache_tags import REDIRECT_TAG
from tracardi.service.cache_change_tagger.change_tagger import invalidate_cache_on_update
from tracardi.service.storage.mysql.mapping.event_redirect_mapping import map_to_event_redirect
from tracardi.service.storage.mysql.service.event_redirect_service import EventRedirectService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

ers = EventRedirectService()

def _records(records: SelectResult) -> Tuple[List[EventRedirect], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_event_redirect)), records.count()


async def load_all(search: str, offset: int = None, limit: int = None) -> Tuple[List[EventRedirect], int]:
    return _records(await ers.load_all(search, limit, offset))


async def load_by_id(event_redirect_id: str) -> Optional[EventRedirect]:
    record = await ers.load_by_id(event_redirect_id)
    if not record.exists():
        return None

    return record.map_to_object(map_to_event_redirect)


async def delete_by_id(event_redirect_id: str) -> Tuple[bool, Optional[EventRedirect]]:
    with invalidate_cache_on_update(*REDIRECT_TAG):
        return await ers.delete_by_id(event_redirect_id)


async def insert(event_redirect: EventRedirect):
    with invalidate_cache_on_update(*REDIRECT_TAG):
        return await ers.insert(event_redirect)
