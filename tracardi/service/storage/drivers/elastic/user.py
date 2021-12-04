from tracardi.service.storage.factory import storage_manager
from uuid import UUID


async def add_user(user):
    return await storage_manager("user").upsert(replace_id=True, data=user.encode(salt="6qO.IwmWg=#..R7/zICi").dict())


async def del_user(id: UUID):
    return await storage_manager("user").delete(id)