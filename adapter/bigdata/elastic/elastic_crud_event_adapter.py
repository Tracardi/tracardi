from typing import Optional

from adapter.bigdata.elastic.logging.logger import get_logger
from tracardi.domain.event import Event
from adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from adapter.bigdata.elastic.helpers.crud_event_helper import load_event, delete_by_id

logger = get_logger(__name__)


class ElasticCrudEventAdapter(ElasticAdapter):

    async def load_event_from_db(self, event_id: str) -> Optional[Event]:
        event_record = await load_event(self._client, event_id)

        if event_record is None:
            return None
        return event_record.to_entity(Event)

    async def delete_event_from_db(self, event_id):
        return await delete_by_id(self._client, event_id)

    async def count_events_in_db(self, query: dict = None):
        return await self.core.count('event', query)
