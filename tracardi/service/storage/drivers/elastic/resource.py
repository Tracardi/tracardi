from tracardi.domain.entity import Entity
from tracardi.service.storage.factory import StorageFor
from typing import List, Tuple
from tracardi.domain.resource import Resource, ResourceRecord
from tracardi.service.storage.factory import storage_manager, StorageForBulk


async def refresh():
    return await storage_manager('resource').refresh()


async def flush():
    return await storage_manager('resource').flush()


async def load_all() -> Tuple[List[Resource], int]:
    result = await StorageForBulk().index('resource').load()
    data = [ResourceRecord.construct(Resource.__fields_set__, **r).decode() for r in result]
    return data, result.total


async def load_record(id: str) -> ResourceRecord:
    return await StorageFor(Entity(id=id)).index("resource").load(ResourceRecord)


async def load(id: str) -> Resource:
    resource_config_record = await load_record(id)  # type: ResourceRecord
    if resource_config_record is None:
        raise ValueError('Resource id {} does not exist.'.format(id))

    return resource_config_record.decode()


async def delete(id: str):
    return await StorageFor(Entity(id=id)).index("resource").delete()
