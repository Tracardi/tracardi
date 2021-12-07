from pydantic import BaseModel


class Configuration(BaseModel):
    pattern: str
    text: str
    group_prefix: str = "Group"
