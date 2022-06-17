from typing import List, Optional
from pydantic import BaseModel, validator
import json

from tracardi.domain.named_entity import NamedEntity


class Configuration(BaseModel):
    debug: bool = False
    event_types: List[NamedEntity] = []

    profile_less: Optional[bool] = False
    session_less: Optional[bool] = False
    properties: Optional[str] = "{}"
    event_id: Optional[str] = None
    event_type: Optional[NamedEntity] = None

    @validator("properties")
    def convert_to_json_id_dict(cls, value):
        if isinstance(value, dict):
            value = json.dumps(value)
        return value

    def get_allowed_event_types(self) -> List[str]:
        return [event.id for event in self.event_types]
