from tracardi.config import memory_cache
from tracardi.service.decorators.function_memory_cache import async_cache_for
from tracardi.domain.resource import Resource
from tracardi.service.storage.mysql.interface import resource_dao


@async_cache_for(memory_cache.resource_load_cache_ttl, timeout=.5)
async def load_resource_via_cache(resource_id: str) -> Resource:
    return await resource_dao.load_resource_by_id_with_error(resource_id)
