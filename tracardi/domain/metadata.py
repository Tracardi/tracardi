from typing import Optional

from pydantic import BaseModel

from tracardi.domain.geo import Geo
from tracardi.domain.time import Time, ProfileTime


class Metadata(BaseModel):
    time: Time


class ProfileMetadata(BaseModel):
    time: ProfileTime
    aux: Optional[dict] = {}
    status: Optional[str] = None


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
    geo: Optional[Geo] = Geo.construct()
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
