from typing import Optional, List

from tracardi.domain.entity import Entity
from tracardi.domain.entity_record import EntityRecord, EntityRecordMetadata, EntityRecordTime
from tracardi.domain.remote_system_integration_id import RemoteSystemIntegrationId
from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.elastic.interface import entity as entity_db
from tracardi.service.storage.elastic.driver.factory import storage_manager
from tracardi.service.utils.date import now_in_utc


async def _load_by_values(field_value_pairs: List[tuple]) -> StorageRecords:
    return await storage_manager('entity').load_by_values(field_value_pairs)


async def commit_integration_ids():
    await entity_db.refresh()


async def load_integration_id(profile_id, system_name) -> List[RemoteSystemIntegrationId]:
    field_value_pairs = [('type', system_name), ('profile.id', profile_id)]
    result = await _load_by_values(field_value_pairs)
    return result.to_domain_objects(RemoteSystemIntegrationId)


async def save_integration_id(profile_id, system_name, remote_id, data: Optional[dict] = None):
    if data is None:
        data = {}

    record = EntityRecord(
        metadata=EntityRecordMetadata(
            time=EntityRecordTime(
                insert=now_in_utc(),
                update=now_in_utc()
            )
        ),
        id=f"{system_name}:{profile_id}",
        type=system_name,
        profile=Entity(id=profile_id),
        properties=data,
        traits={
            "id": remote_id
        }
    )

    return await entity_db.upsert(record)
