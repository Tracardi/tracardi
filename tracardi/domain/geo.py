from typing import Optional, List, Any, Tuple

from pydantic import BaseModel


class Country(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None

    def __eq__(self, other):
        return self.name == other.name and self.code == other.code


class Geo(BaseModel):
    country: Optional[Country] = Country()
    city: Optional[str] = None
    county: Optional[str] = None
    postal: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location: Optional[Tuple[float, float]] = None

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.has_lon_lat():
            self.location = (self.longitude, self.latitude)


    def is_empty(self) -> bool:
        return self.country.name is None

    def has_lon_lat(self) -> bool:
        return self.latitude is not None and self.latitude is not None

    def __eq__(self, other):
        return self.country == other.country and self.city == other.city and self.county == other.county \
               and self.postal == other.postal and self.latitude == other.latitude and self.longitude == other.longitude
