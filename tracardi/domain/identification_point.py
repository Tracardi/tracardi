from typing import Optional, List

from pydantic import BaseModel

from tracardi.domain.named_entity import NamedEntity, NamedEntityInContext
from tracardi.domain.ref_value import RefValue


class IdentificationField(BaseModel):
    profile_trait: RefValue
    event_property: RefValue


class IdentificationPoint(NamedEntityInContext):
    description: Optional[str] = ""
    source: NamedEntity
    event_type: NamedEntity
    fields: List[IdentificationField]
    enabled: bool = False
    settings: Optional[dict] = {}
