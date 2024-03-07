from tracardi.service.decorators.function_memory_cache import async_cache_for
from tracardi.domain.resource import Resource
from tracardi.service.domain import resource as resource_db

@async_cache_for(5)
async def load_resource(resource_id: str) -> Resource:
    return await resource_db.load(resource_id)