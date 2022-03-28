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

    def has_roles(self, roles) -> bool:
        return len(set(self.roles).intersection(set(roles))) > 0

    def is_the_same_user(self, id):
        return self.id == id

    def is_admin(self):
        return "admin" in self.roles

