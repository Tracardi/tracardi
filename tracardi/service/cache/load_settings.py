from tracardi.config import memory_cache
from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.service.storage.mysql.service.configuration_service import ConfigurationService


@AsyncCache(60,
            timeout=5,
            max_one_cache_fill_every=memory_cache.max_one_cache_fill_every,
            return_cache_on_error=True)
async def load_global_settings_by_key(key):
    cs = ConfigurationService()
    return await cs.load_by_id(key)