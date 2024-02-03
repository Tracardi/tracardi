from typing import Optional

from tracardi.domain.entity import Entity
from tracardi.domain.entity_record import EntityRecord, EntityRecordMetadata, EntityRecordTime
from tracardi.domain.remote_system_integration_id import RemoteSystemIntegrationId
from tracardi.service.storage.driver.elastic import entity as entity_db
from tracardi.service.utils.date import now_in_utc


async def load_integration_id(profile_id, system_name):
    result = await entity_db.load_by_values([('type', system_name), ('profile.id', profile_id)])
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

    await entity_db.upsert(record)