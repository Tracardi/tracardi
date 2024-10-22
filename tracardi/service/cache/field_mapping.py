from tracardi.service.decorators.async_cache import AsyncCache
from tracardi.service.storage.elastic.driver.factory import storage_manager


@AsyncCache(5,
            timeout=.5,
            max_one_cache_fill_every=.1,
            return_cache_on_error=True
            )
async def load_fields(index: str) -> list:
    mapping = await storage_manager(index).get_mapping()
    return mapping.get_field_names()
