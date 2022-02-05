from typing import Union

from pydantic import BaseModel


class GeoPosition(BaseModel):
    lat: Union[float, str]
    lng: Union[float, str]


class Configuration(BaseModel):
    start_coordinate: GeoPosition
    end_coordinate: GeoPosition
