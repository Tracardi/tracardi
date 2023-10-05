from typing import Optional

from pydantic import BaseModel


class RemoteApiResource(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    url: str  # AnyHttpUrl
