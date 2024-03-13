from typing import List, Optional, Tuple, Dict

from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.rule import Rule
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache.trigger import load_trigger_rule
from tracardi.service.storage.mysql.mapping.workflow_trigger_mapping import map_to_workflow_trigger_table, \
    map_to_workflow_trigger_rule
from tracardi.service.storage.mysql.schema.table import WorkflowTriggerTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context

logger = get_logger(__name__)

class WorkflowTriggerService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(WorkflowTriggerTable, search, limit, offset)

    async def load_by_id(self, trigger_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(WorkflowTriggerTable, primary_id=trigger_id)

    async def delete_by_id(self, trigger_id: str) ->  Tuple[bool, Optional[Rule]]:
        return await self._delete_by_id_in_deployment_mode(WorkflowTriggerTable,
                                                           map_to_workflow_trigger_rule,
                                                           primary_id=trigger_id)


    async def delete_by_workflow_id(self, workflow_id: str) -> str:
        where = where_tenant_and_mode_context(
            WorkflowTriggerTable,
            WorkflowTriggerTable.flow_id == workflow_id
        )
        return await self._delete_query(WorkflowTriggerTable, where=where)

    async def insert(self, workflow_trigger: Rule):
        return await self._replace(WorkflowTriggerTable, map_to_workflow_trigger_table(workflow_trigger))

    # Custom

    async def load_by_workflow(self,
                               workflow_id: str,
                               limit: int = None,
                               offset: int = None, ) -> SelectResult:
        where = where_tenant_and_mode_context(
            WorkflowTriggerTable,
            WorkflowTriggerTable.flow_id == workflow_id
        )

        return await self._select_in_deployment_mode(WorkflowTriggerTable,
                                                     where=where,
                                                     limit=limit,
                                                     offset=offset)

    async def load_rule(self, event_type_id, source_id):
        where = where_tenant_and_mode_context(
            WorkflowTriggerTable,
            WorkflowTriggerTable.event_type_id == event_type_id,
            WorkflowTriggerTable.source_id == source_id,
            WorkflowTriggerTable.enabled == True
        )

        return await self._select_in_deployment_mode(
            WorkflowTriggerTable,
            where=where
        )

    @staticmethod
    def _get_cache_key(source_id, event_type):
        return f"rules-{source_id}-{event_type}"

    async def _get_rules_for_source_and_event_type(self, source: Entity, events: List[Event]) -> Tuple[
        Dict[str, List[Rule]], bool]:

        # Get event types for valid events

        event_types = {event.type for event in events if event.metadata.valid}

        # Cache rules per event types

        event_type_rules = {}
        has_routes = False
        for event_type in event_types:

            routes: List[Rule] = await load_trigger_rule(self, event_type, source.id)

            # TODO remove 01-04-2024
            # cache_key = self._get_cache_key(source.id, event_type)
            # if cache_key not in memory_cache:
            #     logger.debug("Loading routing rules for cache key {}".format(cache_key))
            #     rules: List[Rule] = await load_trigger_rule(event_type, source.id)
            #
            #     memory_cache[cache_key] = CacheItem(data=rules,
            #                                         ttl=memory_cache_config.trigger_rule_cache_ttl)
            #
            # routes = list(memory_cache[cache_key].data)

            if not has_routes and routes:
                has_routes = True

            event_type_rules[event_type] = routes

        return event_type_rules, has_routes

    @staticmethod
    def _read_rule(event_type_id: str, rules: Dict[str, List[Rule]]) -> List[Rule]:
        if event_type_id not in rules:
            return []

        return rules[event_type_id]

    async def load_by_source_and_events(self, source: Entity, events: List[Event]) -> Optional[List[Tuple[List[Rule], Event]]]:
        rules, has_routing_rules = await self._get_rules_for_source_and_event_type(source, events)

        if not has_routing_rules:
            return None

        return [(self._read_rule(event.type, rules), event) for event in events]

    async def load_by_event_type(self, event_type_id: str, limit: int = 100) -> SelectResult:
        where = where_tenant_and_mode_context(
            WorkflowTriggerTable,
            WorkflowTriggerTable.event_type_id == event_type_id
        )

        return await self._select_in_deployment_mode(
            WorkflowTriggerTable,
            where=where,
            limit=limit)

    async def load_by_segment(self, segment_id: str, limit: int = 100) -> SelectResult:
        where = where_tenant_and_mode_context(
            WorkflowTriggerTable,
            WorkflowTriggerTable.segment_id == segment_id
        )

        return await self._select_in_deployment_mode(
            WorkflowTriggerTable,
            where=where,
            limit=limit)
