from pydantic import BaseModel


class Configuration(BaseModel):
    id: str
    type: str
