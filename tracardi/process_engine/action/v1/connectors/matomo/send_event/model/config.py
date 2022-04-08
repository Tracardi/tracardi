from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity
from typing import Optional, Union
import random


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
    send_image: Optional[int] = 0
    idsite: int
    rec: Optional[int] = 1
    action_name: str
    url: str
    _id: str
    rand: Optional[int] = random.randint(0, 1000)
    apiv: Optional[int] = 1
    urlref: Optional[str] = None
    _idvc: int
    _viewts: int
    _idts: int
    _rcn: Optional[str] = None
    _rck: Optional[str] = None
    res: str
    cookie: Optional[int] = 0
    ua: Optional[str] = None
    lang: Optional[str] = None
    uid: str
    new_visit: int
    search: Optional[str] = None
    search_cat: Optional[str] = None
    search_count: Optional[int] = None
    pv_id: str
    idgoal: Optional[int] = None
    revenue: Optional[Union[float, int]] = None
    gt_ms: int

    def to_dict(self):
        return {key: value for key, value in self.dict().items() if value is not None}
