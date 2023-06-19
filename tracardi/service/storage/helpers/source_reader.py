from tracardi.domain.resource import Resource
from tracardi.service.storage.driver.storage.driver import resource as resource_db


async def read_source(resource_id: str) -> Resource:
    return await resource_db.load(resource_id)
