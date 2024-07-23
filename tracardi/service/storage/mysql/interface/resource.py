from typing import Tuple, List, Optional

from tracardi.domain.resource import Resource
from tracardi.service.license import License
from tracardi.service.storage.mysql.map_to_named_entity import map_to_named_entity
from tracardi.service.storage.mysql.mapping.resource_mapping import map_to_resource
from tracardi.service.storage.mysql.service.resource_service import ResourceService

rs = ResourceService()


def _records(records, mapper) -> Tuple[List[Resource], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(mapper)), records.count()


async def load_resource_by_id(resource_id: str) -> Optional[Resource]:
    record = await rs.load_by_id(resource_id)
    return record.map_to_object(map_to_resource)


async def load_resource_by_id_with_error(resource_id: str) -> Resource:
    resource = (await rs.load_by_id(resource_id)).map_to_object(map_to_resource)

    if resource is None:
        raise ValueError(f'Resource id {resource_id} does not exist.')

    if not resource.enabled:
        raise ValueError(f'Resource id {resource_id} disabled.')

    return resource


async def load_all_resources(search: str = None, limit: int = None, offset: int = None) -> Tuple[List[Resource], int]:
    records = await rs.load_all(search, limit, offset)
    return _records(records, map_to_resource)


async def load_all_resource_entities(search: str = None, limit: int = None, offset: int = None) -> Tuple[
    List[Resource], int]:
    records = await rs.load_all(search, limit, offset)
    return _records(records, map_to_named_entity)


async def load_resources_entities_by_tag(tag: str) -> Tuple[List[Resource], int]:
    records = await rs.load_enabled_by_tag(tag)
    return _records(records, map_to_named_entity)


async def list_resources_with_destinations():
    records = await rs.load_resource_with_destinations()

    result = {}
    for resource in records.map_to_objects(map_to_resource):
        if resource.is_destination():
            if resource.destination.pro is True and not License.has_license():
                continue
            result[resource.id] = resource
    return result


async def insert_resource(resource: Resource):
    return await rs.insert(resource)


async def delete_resource_by_id(resource_id: str):
    await rs.delete_by_id(resource_id)
