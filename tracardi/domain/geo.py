from typing import Optional

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

    def is_empty(self) -> bool:
        return self.country.name is None

    def __eq__(self, other):
        return self.country == other.country and self.city == other.city and self.county == other.county \
               and self.postal == other.postal and self.latitude == other.latitude and self.longitude == other.longitude
