from pydantic import BaseModel


class FullContactSourceConfiguration(BaseModel):
    token: str
