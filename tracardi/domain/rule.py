from typing import Optional, Any, List, Set

from pydantic import field_validator, PrivateAttr

from .metadata import Metadata
from .named_entity import NamedEntity, NamedEntityInContext
from .time import Time
from ..service.utils.date import now_in_utc


class Rule(NamedEntityInContext):

    _schedule_node_id: str = PrivateAttr(None)
    event_type: Optional[NamedEntity] = NamedEntity(id="", name="")
    type: Optional[str] = 'event-collect'
    flow: NamedEntity
    source: Optional[NamedEntity] = NamedEntity(id="", name="")
    segment: Optional[NamedEntity] = NamedEntity(id="", name="")
    enabled: Optional[bool] = True
    description: Optional[str] = "No description provided"
    properties: Optional[dict] = None
    metadata: Optional[Metadata] = None
    tags: Optional[List[str]] = ["General"]

    @field_validator("tags")
    @classmethod
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
                    insert=now_in_utc()
                ))
        super().__init__(**data)
