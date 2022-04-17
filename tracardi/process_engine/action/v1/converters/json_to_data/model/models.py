from pydantic import BaseModel


class Configuration(BaseModel):
    to_data: str
