from pydantic import BaseModel


class ThirdPartyProcessor(BaseModel):
    url: str
    description: str
