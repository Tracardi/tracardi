from pydantic import BaseModel


class GeoPosition(BaseModel):
    lat: float
    lng: float


class Configuration(BaseModel):
    center_coordinate: GeoPosition
    test_coordinate: GeoPosition
    radius: float
