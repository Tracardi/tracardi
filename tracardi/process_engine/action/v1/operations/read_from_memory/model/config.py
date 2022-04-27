from pydantic import BaseModel


class Config(BaseModel):
    key: str
