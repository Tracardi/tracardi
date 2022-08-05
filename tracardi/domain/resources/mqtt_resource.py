from typing import Optional

from pydantic import BaseModel


class MqttResourceCredentials(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    url: str
    port: Optional[int] = 1883
