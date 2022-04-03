from pydantic import BaseModel


class Configuration(BaseModel):
    property: str
