from pydantic import BaseModel


class TrelloCredentials(BaseModel):
    api_key: str
    token: str
