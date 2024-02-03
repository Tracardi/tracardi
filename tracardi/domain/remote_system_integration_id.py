from typing import Optional

from tracardi.domain.entity import Entity
from tracardi.domain.entity_record import EntityRecordMetadata


class RemoteSystemIntegrationId(Entity):
    profile: Entity
    metadata: Optional[EntityRecordMetadata] = EntityRecordMetadata()
    traits: Optional[dict] = {}