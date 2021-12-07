from pydantic import BaseModel


class Configuration(BaseModel):
    validator: str
    data: str




