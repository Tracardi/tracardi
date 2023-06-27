from datetime import datetime
from typing import Optional, Any, List, Set

from pydantic import validator, PrivateAttr

from .metadata import Metadata
from .named_entity import NamedEntity
from .time import Time
from .value_object.storage_info import StorageInfo


class Rule(NamedEntity):

    _schedule_node_id: str = PrivateAttr(None)
    event_type: NamedEntity
    type: Optional[str] = 'workflow'
    flow: NamedEntity
    source: NamedEntity
    enabled: Optional[bool] = True
    description: Optional[str] = "No description provided"
    properties: Optional[dict] = None
    metadata: Optional[Metadata]
    tags: Optional[List[str]] = ["General"]

    @validator("tags")
    def tags_can_not_be_empty(cls, value):
        if len(value) == 0:
            value = ["General"]
        return value

    def set_as_scheduled(self, schedule_node_id):
        self._schedule_node_id = schedule_node_id

    def schedule_node_id(self):
        return self._schedule_node_id

    def are_consents_met(self, profile_consent_ids: Set[str]) -> bool:
        if self.properties is None:
            # No restriction
            return True

        if not profile_consent_ids:
            # No consents set on profile
            return True

        if 'consents' in self.properties and isinstance(self.properties['consents'], list):
            if len(self.properties['consents']) > 0:
                required_consent_ids = set([item['id'] for item in self.properties['consents'] if 'id' in item])
                return required_consent_ids.intersection(profile_consent_ids) == required_consent_ids

        return True

    def __init__(self, **data: Any):
        if 'metadata' not in data:
            data['metadata'] = Metadata(
                time=Time(
                    insert=datetime.utcnow()
                ))
        super().__init__(**data)

    @staticmethod
    def storage_info() -> StorageInfo:
        return StorageInfo(
            'rule',
            Rule
        )
