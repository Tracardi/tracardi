from typing import Tuple, List, Optional

from tracardi.domain.remote_system_integration_id import RemoteSystemIntegrationId
from tracardi.service.storage.elastic.dal.entity import _unique_entity_types
from tracardi.service.storage.elastic.dal import entity as entity_dal
from tracardi.service.storage.elastic.dal.integration_id import save_integration_id, load_integration_id


async def load_entity_types() -> Tuple[List[dict], int]:
    # Returns only 800 types
    result = await _unique_entity_types(bucket_name="type", buckets_size=800)
    return [{
        "id": key,
        "name": key
    } for key, _ in result.aggregations['type'][0].items() if key != "other"], result.total


async def delete_by_id(entity_id: str) -> dict:
    return await entity_dal.delete_by_id(entity_id)


async def upsert(record):
    # TODO return raw data
    return await entity_dal.upsert(record)


async def save_integration_id_in_entity(profile_id, system_name, remote_id, data: Optional[dict] = None):
    # Return void
    await save_integration_id(profile_id, system_name, remote_id, data)


async def load_integration_id_from_entity(profile_id, system_name) -> List[RemoteSystemIntegrationId]:
    result = await load_integration_id(profile_id, system_name)
    return result.to_domain_objects(RemoteSystemIntegrationId)