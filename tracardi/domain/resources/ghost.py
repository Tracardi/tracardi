from pydantic import BaseModel

class GhostResourceCredentials(BaseModel):
    api_url: str
    api_key: str
