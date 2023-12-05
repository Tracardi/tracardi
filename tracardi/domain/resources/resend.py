from pydantic import BaseModel


class ResendResource(BaseModel):
    api_key: str
