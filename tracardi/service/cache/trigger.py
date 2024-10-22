from typing import List

from tracardi.config import memory_cache
from tracardi.domain.rule import Rule
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.service.storage.mysql.mapping.workflow_trigger_mapping import map_to_workflow_trigger_rule


def _cache_param_function(wfr, event_type: str, source_id: str) -> tuple:
    return event_type, source_id


@AsyncCache(memory_cache.trigger_rule_cache_ttl, key_func=_cache_param_function, timeout=.5, max_one_cache_fill_every=.1)
async def load_trigger_rule(wts, event_type: str, source_id: str) -> List[Rule]:
    records = await wts.load_rule(event_type, source_id)
    return list(records.map_to_objects(map_to_workflow_trigger_rule))
