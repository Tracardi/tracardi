from pydantic import BaseModel, validator
from tracardi.domain.named_entity import NamedEntity
from typing import Optional, Union, Dict, Any
import random


class Config(BaseModel):
    source: NamedEntity
    site_id: int
    url_ref: Optional[str] = None
    rcn: Optional[str] = None
    rck: Optional[str] = None
    search_keyword: Optional[str] = None
    search_category: Optional[str] = None
    search_results_count: Optional[str] = None
    goal_id: Optional[str] = None
    revenue: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = {}

    @validator("dimensions")
    def validate_dimensions(cls, value):
        for key in value:
            if not key.startswith("dimension"):
                raise ValueError("Every dimension parameter has to start with 'dimension', e.g. 'dimension3'")
        return value


class MatomoPayload(BaseModel):
    cip: str
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
    gt_ms: Optional[int] = None
    dimensions: Optional[Dict[str, Any]]
    pf_net: Optional[int] = None
    pf_srv: Optional[int] = None
    pf_tfr: Optional[int] = None
    pf_dm1: Optional[int] = None
    pf_dm2: Optional[int] = None
    pf_onl: Optional[int] = None

    @validator("pf_net", "pf_srv", "pf_tfr", "pf_dm1", "pf_dm2", "pf_onl")
    def validate_performance_values(cls, value):
        if value == 0:
            value = None
        return value

    def to_dict(self):
        return {
            key: value for key, value in {**self.dict(), **self.dimensions}.items()
            if value is not None and key != "dimensions"
        }
