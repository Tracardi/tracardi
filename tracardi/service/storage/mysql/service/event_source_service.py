import logging
from sqlalchemy import and_

from tracardi.config import tracardi
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_source_mapping import map_to_event_source_table
from tracardi.service.storage.mysql.schema.table import EventSourceTable
from tracardi.service.storage.mysql.service.table_service import TableService, where_tenant_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventSourceService(TableService):


    async def load_all(self) -> SelectResult:
        return await self._load_all(EventSourceTable)

    async def load_by_id(self, source_id: str) -> SelectResult:
        return await self._load_by_id(
            EventSourceTable,
            primary_id=source_id)


    async def load_by_tag(self, tag: str) -> SelectResult:
        # Todo filters if only one tag
        return await self._field_filter(
            EventSourceTable,
            field=EventSourceTable.tags,
            value=tag
        )

    async def load_by_bridge(self, bridge_id: str) -> SelectResult:
        return await self._field_filter(
            EventSourceTable,
            field=EventSourceTable.bridge_id,
            value=bridge_id
        )

    async def load_by_type(self, type: str) -> SelectResult:
        return await self._field_filter(
            EventSourceTable,
            field=EventSourceTable.type,
            value=type
        )

    async def load_active_by_bridge_id(self, bridge_id: str) -> SelectResult:
        return await self._where(
            EventSourceTable,
            where=where_tenant_context(
                EventSourceTable,
                EventSourceTable.bridge_id == bridge_id,
                EventSourceTable.enabled ==  True
            )
        )

    async def delete_by_id(self, source_id: str) -> str:
        return await self._delete_by_id(EventSourceTable, primary_id=source_id)

    async def insert(self, event_source: EventSource):
        return await self._insert_if_none(EventSourceTable, map_to_event_source_table(event_source))

    async def lock_by_bridge_id(self, bridge_id: str, lock):
        return await self._update_by_query(
            EventSourceTable,
            where=(
                where_tenant_context(
                    EventSourceTable,
                    EventSourceTable.bridge_id == bridge_id
                )
            ),
            new_data={
                'locked': lock
            }
        )

    @staticmethod
    def event_source_types():
        standard_inbound_sources = {
            "imap": {
                "name": "IMAP Bridge",
                "tags": ["imap", "inbound"]
            },
            "mqtt": {
                "name": "MQTT Bridge",
                "tags": ["mqtt", "inbound"]
            },
            "queue": {
                "name": "Queue Bridge",
                "tags": ["queue", "inbound"]
            },
            "rest": {
                "name": "Rest Api Call",
                "tags": ["rest", "inbound"]
            },
            "redirect": {
                "name": "Redirect Link",
                "tags": ["link", "inbound"]
            },
            "webhook": {
                "name": "Webhook",
                "tags": ["webhook", "inbound"]
            },
            "internal": {
                "name": "Internal",
                "tags": ["internal", "inbound"]
            },
        }

        return standard_inbound_sources

    async def save(self, event_source: EventSource):
        types = EventSourceService.event_source_types()
        if event_source.is_allowed(types):
            return await self._replace(EventSourceTable, map_to_event_source_table(event_source))
        else:
            raise ValueError(f"Unknown event source types {event_source.type}. Available {types}.")