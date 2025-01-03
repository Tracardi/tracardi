from typing import Optional, Dict

from pydantic import BaseModel

from tracardi.domain.geo import Geo
from tracardi.domain.time import Time, ProfileTime
from tracardi.common.time.date import now_in_utc


class Metadata(BaseModel):
    time: Time


class ProfileSystemMetadata(BaseModel):
    integrations: Optional[dict] = {}
    aux: Optional[dict] = {}

    def has_merging_data(self) -> bool:
        return 'auto_merge' in self.aux and isinstance(self.aux['auto_merge'], list) and len(self.aux['auto_merge']) > 0

    def remove_merging_data(self):
        if 'auto_merge' in  self.aux:
            del (self.aux['auto_merge'])

    def set_auto_merge_fields(self, auto_merge_ids: set):
        if 'auto_merge' not in self.aux or not isinstance(self.aux['auto_merge'], list):
            self.aux['auto_merge'] = list(auto_merge_ids)
        else:
            self.aux['auto_merge'] = list(set(self.aux['auto_merge']).union(auto_merge_ids))

    def get_auto_merge_fields(self):
        return self.aux.get('auto_merge', [])

    def reset_auto_merge_fields(self):
        self.aux['auto_merge'] = []
        self.aux['merge_time'] = now_in_utc()


class ProfileMetadata(BaseModel):
    time: ProfileTime
    aux: Optional[dict] = {}
    status: Optional[str] = None
    fields: Optional[Dict['str', list]] = {}
    system: Optional[ProfileSystemMetadata] = ProfileSystemMetadata()


class OS(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None


class Device(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    type: Optional[str] = None
    touch: Optional[bool] = False
    ip: Optional[str] = None
    resolution: Optional[str] = None
    geo: Optional[Geo] = Geo.model_construct()
    color_depth: Optional[int] = None
    orientation: Optional[str] = None


class Application(BaseModel):
    type: Optional[str] = None  # Browser, App1
    name: Optional[str] = None
    version: Optional[str] = None
    language: Optional[str] = None
    bot: Optional[bool] = False
    resolution: Optional[str] = None


class Hit(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    referer: Optional[str] = None
    query: Optional[str] = None
    category: Optional[str] = None
