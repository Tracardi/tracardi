from typing import Optional

from pydantic import field_validator, BaseModel
from pydantic.networks import AnyHttpUrl

GITHUB_DEFAULT_API_URL = 'https://api.github.com'


class GitHub(BaseModel):
    api_url: AnyHttpUrl
    personal_access_token: Optional[str] = None

    @field_validator("api_url")
    @classmethod
    def normalize_url(cls, value):
        return value.rstrip('/')
