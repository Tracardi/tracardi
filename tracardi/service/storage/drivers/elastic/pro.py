from typing import Optional

from tracardi.domain.entity import Entity
from tracardi.domain.sign_up_data import SignUpData
from tracardi.service.storage.factory import storage_manager, StorageFor


async def read_pro_service_endpoint() -> Optional[SignUpData]:
    return await StorageFor(Entity(id="0")).index("tracardi-pro").load(SignUpData)


async def save_pro_service_endpoint(sign_up_data: SignUpData):
    return await storage_manager("tracardi-pro").upsert(sign_up_data.dict())


async def delete_pro_service_endpoint():
    return await StorageFor(Entity(id="0")).index("tracardi-pro").delete()


async def refresh():
    return await storage_manager('tracardi-pro').refresh()
