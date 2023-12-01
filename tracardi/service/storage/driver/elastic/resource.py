from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from typing import List, Tuple, Optional
from tracardi.domain.resource import Resource, ResourceRecord
from tracardi.service.storage.factory import storage_manager
from tracardi.service.storage.mysql.mapping.resource_mapping import map_to_resource
from tracardi.service.storage.mysql.service.resource_service import ResourceService

rs = ResourceService()


async def save_record(resource: Resource):
    return await rs.insert(resource)

async def load(id: str) -> Resource:

    resource = (await rs.load_by_id(id)).map_to_object(map_to_resource)

    if resource is None:
        raise ValueError('Resource id {} does not exist.'.format(id))

    if not resource.enabled:
        raise ValueError('Resource id {} disabled.'.format(id))

    return resource
