from typing import List, Optional

from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.domain.named_entity import NamedEntity
from tracardi.domain.ref_value import RefValue


class ConsentFieldComplianceSetting(BaseModel):
    action: str  # Remove, Hash, Do nothing
    field: RefValue
    consents: List[NamedEntity]


class ConsentFieldCompliance(Entity):
    name: str
    description: Optional[str] = ""
    event_type: NamedEntity
    settings: List[ConsentFieldComplianceSetting]  # Flattened ES field
    enabled: Optional[bool] = False
