from typing import Optional

from pydantic import BaseModel, AnyHttpUrl


class RemoteApiResource(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    url: AnyHttpUrl
