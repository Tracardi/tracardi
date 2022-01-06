from typing import Optional

from pydantic import AnyHttpUrl, BaseModel


class DiscordWebHookConfiguration(BaseModel):
    url: AnyHttpUrl
    timeout: int = 10
    message: str
    username: Optional[str] = None

