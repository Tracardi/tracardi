from typing import Optional, Dict, Set

from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.domain.geo import Geo
from tracardi.domain.time import Time, ProfileTime


class Metadata(BaseModel):
    time: Time

class ProfileSystemIntegrations(Entity):
    data: Optional[dict] = {}

class ProfileSystemMetadata(BaseModel):
    integrations: Optional[Dict[str, ProfileSystemIntegrations]] = {}
    aux: Optional[dict] = {}

    def has_merging_data(self) -> bool:
        return 'auto_merge' in self.aux and isinstance(self.aux['auto_merge'], list) and len(self.aux['auto_merge'])>0

    def remove_merging_data(self):
        del(self.aux['auto_merge'])

    def set_auto_merge_fields(self, auto_merge_ids):
        if 'auto_merge' not in self.aux or not isinstance(self.aux['auto_merge'], list):
            self.aux['auto_merge'] = list(auto_merge_ids)
        else:
            self.aux['auto_merge'] = list(set(self.aux['auto_merge']).union(auto_merge_ids))

    def get_auto_merge_fields(self):
        return self.aux.get('auto_merge', [])

    def has_integration(self, system: str) -> bool:
        return system in self.integrations and 'id' in self.integrations[system]
    
    def set_integration(self, system: str, id: str, data:Optional [dict]=None):
        if data is None:
            data = {}

        if system not in self.integrations:
            self.integrations[system] = ProfileSystemIntegrations(id = id, data=data)
        else:
            self.integrations[system].id = id
            if data:
                self.integrations[system].data = data

class ProfileMetadata(BaseModel):
    time: ProfileTime
    aux: Optional[dict] = {}
    status: Optional[str] = None
    fields: Optional[dict] = {}
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
