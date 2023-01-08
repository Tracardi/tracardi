from typing import Dict, List

from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity


class ConsentFieldComplianceSetting(BaseModel):
    field: str
    consent_id: str
    action: str  # Remove, Hash, Do nothing


class ConsentFieldCompliance(Entity):
    name: str
    event_type: NamedEntity
    settings: List[ConsentFieldComplianceSetting]
