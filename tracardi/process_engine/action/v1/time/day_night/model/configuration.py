from pydantic import BaseModel


class Configuration(BaseModel):
    latitude: str
    longitude: str
