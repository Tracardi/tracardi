from pydantic import BaseModel


class ClicksendResourceCredentials(BaseModel):
    username: str
    api_key: str
