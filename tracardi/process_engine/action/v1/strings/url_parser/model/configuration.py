from pydantic import BaseModel


class Configuration(BaseModel):
    url: str
