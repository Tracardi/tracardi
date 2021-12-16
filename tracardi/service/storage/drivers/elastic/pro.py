from typing import Optional

from tracardi.domain.entity import Entity

from tracardi.domain.tracardi_pro_endpoint import TracardiProEndpoint
from tracardi.service.storage.factory import storage_manager, StorageFor


async def read_pro_service_endpoint() -> Optional[TracardiProEndpoint]:
    return await StorageFor(Entity(id="0")).index("tracardi-pro").load(TracardiProEndpoint)


async def save_pro_service_endpoint(endpoint: TracardiProEndpoint):
    endpoint.id = "0"
    return await storage_manager("tracardi-pro").upsert(endpoint.dict())


async def delete_pro_service_endpoint():
    return await StorageFor(Entity(id="0")).index("tracardi-pro").delete()


async def refresh():
    return await storage_manager('tracardi-pro').refresh()
