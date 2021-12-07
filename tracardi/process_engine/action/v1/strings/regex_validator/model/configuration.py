from pydantic import BaseModel


class Configuration(BaseModel):
    validation_regex: str
    data: str



