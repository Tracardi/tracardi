from tracardi.domain.resource import ResourceRecord, Resource
from tracardi.domain.entity import Entity

from tracardi.service.storage.factory import StorageFor


async def load_record(id: str) -> ResourceRecord:
    return await StorageFor(Entity(id=id)).index("resource").load(ResourceRecord)


async def load(id: str) -> Resource:
    resource_config_record = await load_record(id)  # type: ResourceRecord
    if resource_config_record is None:
        raise ValueError('Resource id {} does not exist.'.format(id))

    return resource_config_record.decode()


async def delete(id: str):
    return await StorageFor(Entity(id=id)).index("resource").delete()
