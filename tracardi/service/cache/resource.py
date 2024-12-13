from tracardi.config import memory_cache
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.domain.resource import Resource
from tracardi.service.storage.mysql.interface import resource_dao


@AsyncCache(memory_cache.resource_load_cache_ttl,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_resource_via_cache(resource_id: str) -> Resource:
    return await resource_dao.load_resource_by_id_with_error(resource_id)
