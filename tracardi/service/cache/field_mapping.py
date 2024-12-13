from tracardi.config import memory_cache
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.service.storage.elastic.driver.factory import storage_manager


@AsyncCache(5,
            timeout=memory_cache.timeout_sql_query_in,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True
            )
async def load_fields(index: str) -> list:
    mapping = await storage_manager(index).get_mapping()
    return mapping.get_field_names()
