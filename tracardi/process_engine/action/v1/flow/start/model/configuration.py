from pydantic import BaseModel


class Configuration(BaseModel):
    debug: bool = False
