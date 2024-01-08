from dataclasses import dataclass, asdict

from pydantic import field_validator
from tracardi.domain.named_entity import NamedEntity
from typing import Optional, Union, Dict, Any
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
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

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions(cls, value):
        for key in value:
            if not key.startswith("dimension"):
                raise ValueError("Every dimension parameter has to start with 'dimension', e.g. 'dimension3'")
        return value


@dataclass
class MatomoPayload:
    idsite: int
    action_name: str
    _id: str
    url: str
    rand: str
    uid: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None
    cip: Optional[str] = None
    new_visit: Optional[int] = None
    pv_id: Optional[str] = None
    _idvc: Optional[int] = None
    _idts: Optional[int] = None
    _viewts: Optional[int] = None
    send_image: Optional[int] = 0
    rec: Optional[int] = 1
    apiv: Optional[int] = 1
    urlref: Optional[str] = None
    _rcn: Optional[str] = None
    _rck: Optional[str] = None
    res: Optional[str] = None
    cookie: Optional[int] = 0
    ua: Optional[str] = None
    lang: Optional[str] = None
    search: Optional[str] = None
    search_cat: Optional[str] = None
    search_count: Optional[int] = None
    idgoal: Optional[int] = None
    revenue: Optional[Union[float, int]] = None
    gt_ms: Optional[int] = None
    pf_net: Optional[int] = None
    pf_srv: Optional[int] = None
    pf_tfr: Optional[int] = None
    pf_dm1: Optional[int] = None
    pf_dm2: Optional[int] = None
    pf_onl: Optional[int] = None

    def to_dict(self):
        return {
            key: value for key, value in asdict(self).items() if value is not None and key != "dimensions"
        }
