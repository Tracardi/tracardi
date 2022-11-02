from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator
from pydantic.networks import AnyHttpUrl

GITHUB_DEFAULT_API_URL = 'https://api.github.com'


class GitHub(BaseModel):
    api_url: AnyHttpUrl
    personal_access_token: Optional[str] = None

    @validator("api_url")
    def normalize_url(cls, value):
        return value.rstrip('/')
