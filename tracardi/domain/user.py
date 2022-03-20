from typing import List, Optional
from pydantic import BaseModel

from tracardi.service.sha1_hasher import SHA1Encoder


class User(BaseModel):
    id: str
    password: str
    full_name: str
    email: str
    roles: List[str]
    disabled: bool = False
    token: Optional[str] = None

    def encode_password(self):
        self.password = SHA1Encoder.encode(self.password)

