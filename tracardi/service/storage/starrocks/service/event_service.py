from typing import List

from tracardi.domain.event import Event
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.starrocks.mapping.event_mapping import map_to_event_table


class EventService(TableService):

    async def insert(self, event: Event):
        await self._insert(map_to_event_table(event))

    async def insert_many(self, events: List[Event]):
        interests = [map_to_event_table(event) for event in events]
        await self._insert_many(interests)