from pydantic import BaseModel


class Configuration(BaseModel):
    name: str
    value: str
    ttl: int = 30 * 60
    default_value: str
    assign_to_profile: bool = False
