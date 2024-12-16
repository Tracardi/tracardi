from pydantic import BaseModel

class GenAIResourceCredentials(BaseModel):
    api_url: str
    api_key: str
