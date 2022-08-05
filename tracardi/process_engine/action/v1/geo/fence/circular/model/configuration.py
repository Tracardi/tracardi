from typing import Union

from pydantic import BaseModel
from tracardi.service.plugin.domain.config import PluginConfig


class GeoPosition(BaseModel):
    lat: Union[float, str]
    lng: Union[float, str]


class Configuration(PluginConfig):
    center_coordinate: GeoPosition
    test_coordinate: GeoPosition
    radius: float
