from typing import Union

from pydantic import BaseModel


class GeoPosition(BaseModel):
    lat: Union[float, str]
    lng: Union[float, str]


class Configuration(BaseModel):
    center_coordinate: GeoPosition
    test_coordinate: GeoPosition
    radius: float
