from tracardi.domain.resource import Resource
from tracardi.service.storage.driver import storage


async def read_source(resource_id: str) -> Resource:
    return await storage.driver.resource.load(resource_id)
