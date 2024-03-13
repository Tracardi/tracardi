from tracardi.service.decorators.function_memory_cache import async_cache_for
from tracardi.service.storage.factory import storage_manager


@async_cache_for(5)
async def load_fields(index: str) -> list:
    mapping = await storage_manager(index).get_mapping()
    return mapping.get_field_names()