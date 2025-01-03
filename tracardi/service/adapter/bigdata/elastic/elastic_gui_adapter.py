from typing import List, Optional

from tracardi.common.logging.log_handler import get_logger
from tracardi.domain.event import Event
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.service.adapter.bigdata.elastic.helpers.gui_helper import load_profiles_by_segments, \
    get_events_by_session_and_profile, get_events_by_profile, get_events_by_session, unique_field_value

logger = get_logger(__name__)


class ElasticGuiAdapter(ElasticAdapter):

    async def load_profiles_by_segments(self, segments: List[str], condition: str = 'must') -> dict:
        records = await load_profiles_by_segments(segments, condition=condition)
        return records.dict()

    async def load_events_by_session_and_profile(self, profile_id: str, session_id: str, limit: int) -> dict:
        result = await get_events_by_session_and_profile(
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
            "context": doc.get('context', None),
            "tags": doc.get('tags', [])
        } for doc in result]

        return {"result": result, "more_to_load": more_to_load}

    async def load_events_by_profile_id(self, profile_id: str, limit: int) -> dict:
        result = await get_events_by_profile(
            profile_id,
            limit)
        return result.dict()

    async def load_events_by_session(self, session_id: str, limit: int) -> Optional[List[Event]]:
        result = await get_events_by_session(session_id, limit)

        if result.total == 0:
            return None

        return result.to_domain_objects(Event)

    async def load_unique_field_value(self, search_query, limit):
        return await unique_field_value(search_query, limit)
