from typing import Optional

from pydantic import BaseModel


class RedisCredentials(BaseModel):
    url: str
    user: Optional[str] = None
    password: Optional[str] = None
    protocol: Optional[str] = "redis"
    database: Optional[str] = "0"
