from tracardi.service.decorators.function_memory_cache import async_cache_for
from tracardi.service.storage.mysql.service.configuration_service import ConfigurationService


@async_cache_for(60)
async def load_global_settings_by_key(key):
    cs = ConfigurationService()
    return await cs.load_by_id(key)