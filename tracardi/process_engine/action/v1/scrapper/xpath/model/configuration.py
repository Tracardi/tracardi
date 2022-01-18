from pydantic import BaseModel


class Configuration(BaseModel):
    xpath: str
    content: str
