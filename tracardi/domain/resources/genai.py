from pydantic import BaseModel

class genAIResourceCredentials(BaseModel):
    api_url: str
    api_key: str
