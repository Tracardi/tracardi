from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity
from typing import Optional


class Config(BaseModel):
    source: NamedEntity
    urlref: Optional[str] = None
    rck: Optional[str] = None
    rcn: Optional[str] = None
    search: Optional[str] = None
    search_cat: Optional[str] = None
    id_goal: Optional[str] = None
    revenue: Optional[str] = None


class MatomoPayload(BaseModel):
    idsite: int
    rec: Optional[int] = 1
    url: str
    action_name: str

    def to_dict(self):
        return {key: value for key, value in self.dict().items() if value is not None}
