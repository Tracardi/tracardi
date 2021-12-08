from pydantic import BaseModel


class Configuration(BaseModel):
    to_json: str
