from pydantic import BaseModel


class TwitterResourceCredentials(BaseModel):
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
