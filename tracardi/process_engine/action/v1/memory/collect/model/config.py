from pydantic import BaseModel


class Config(BaseModel):
    name: str
    type: str = "list"
