from pydantic import BaseModel


class Config(BaseModel):
    reshape: str = ""
    default: bool = True
