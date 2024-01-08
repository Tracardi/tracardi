from typing import Optional, Dict

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
    
    def has_integration(self, system: str) -> bool:
        return system in self.integrations and 'id' in self.integrations[system]
    
    def set_integration(self, system: str, id: str, data:Optional [dict]=None):
        self.integrations[system].id = id
        if data:
            self.integrations[system].data = data

class ProfileMetadata(BaseModel):
    time: ProfileTime
    aux: Optional[dict] = {}
    status: Optional[str] = None
    fields: Optional[dict] = {}
    system: Optional[ProfileSystemMetadata] = ProfileSystemMetadata()

    def set_fields_timestamps(self, field_timestamp_manager):
        for field, timestamp_data  in field_timestamp_manager.get_timestamps():
            self.fields[field] = timestamp_data


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
