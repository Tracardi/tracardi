from typing import Optional

from pydantic import BaseModel


class Country(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None


class Geo(BaseModel):
    country: Optional[Country] = Country()
    city: Optional[str] = None
    county: Optional[str] = None
    postal: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def is_empty(self) -> bool:
        return self.country.name is None
