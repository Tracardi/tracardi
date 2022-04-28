from pydantic import BaseModel


class Configuration(BaseModel):
    value: str
