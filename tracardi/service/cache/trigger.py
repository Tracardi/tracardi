from typing import List

from tracardi.config import memory_cache
from tracardi.domain.rule import Rule
from tracardi.service.decorators.function_memory_cache import async_cache_for
from tracardi.service.storage.mysql.mapping.workflow_trigger_mapping import map_to_workflow_trigger_rule

@async_cache_for(memory_cache.trigger_rule_cache_ttl)
async def load_trigger_rule(wts, event_type: str, source_id: str) -> List[Rule]:
    records = await wts.load_rule(event_type, source_id)
    return list(records.map_to_objects(map_to_workflow_trigger_rule))