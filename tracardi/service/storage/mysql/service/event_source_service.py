import logging
from typing import Tuple, Optional

from tracardi.config import tracardi
from tracardi.domain.event_source import EventSource
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_source_mapping import map_to_event_source_table, map_to_event_source
from tracardi.service.storage.mysql.schema.table import EventSourceTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context
from tracardi.service.storage.mysql.utils.select_result import SelectResult

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventSourceService(TableService):

    async def load_all_in_deployment_mode(self, search: str = None, limit: int = None,
                                          offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(EventSourceTable, search, limit, offset)

    async def load_by_id_in_deployment_mode(self, source_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(
            EventSourceTable,
            primary_id=source_id
        )

    async def delete_by_id_in_deployment_mode(self, source_id: str) -> Tuple[
        bool, Optional[EventSource]]:
        return await self._delete_by_id_in_deployment_mode(
            EventSourceTable,
            map_to_event_source,
            primary_id=source_id
        )

    async def load_by_type_in_deployment_mode(self, type: str) -> SelectResult:
        where = where_tenant_and_mode_context(EventSourceTable, EventSourceTable.type == type)
        return await self._select_in_deployment_mode(
            EventSourceTable,
            where=where
        )

    async def load_active_by_bridge_id(self, bridge_id: str) -> SelectResult:
        # It is PRODUCTION CONTEXT-LESS
        return await self._select_in_deployment_mode(
            EventSourceTable,
            where=where_tenant_and_mode_context(
                EventSourceTable,
                EventSourceTable.bridge_id == bridge_id,
                EventSourceTable.enabled == True
            )
        )

    async def insert(self, event_source: EventSource):
        return await self._insert_if_none(EventSourceTable, map_to_event_source_table(event_source))

    async def lock_by_bridge_id(self, bridge_id: str, lock):
        # It is PRODUCTION CONTEXT-LESS
        return await self._update_query(
            EventSourceTable,
            where=(
                where_tenant_and_mode_context(
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
        types = self.event_source_types()
        if event_source.is_allowed(types):
            return await self._replace(EventSourceTable, map_to_event_source_table(event_source))
        else:
            raise ValueError(f"Unknown event source types {event_source.type}. Available {types}.")
