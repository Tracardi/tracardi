from typing import List, Optional, Any
from pydantic import BaseModel

from tracardi.service.sha1_hasher import SHA1Encoder
from datetime import datetime


class User(BaseModel):
    id: str
    password: str
    name: str
    email: str
    roles: List[str]
    enabled: bool = False
    preference: Optional[dict] = {}
    expiration_timestamp: Optional[int] = None

    @staticmethod
    def encode_password(password):
        return SHA1Encoder.encode(password)

    def has_roles(self, roles) -> bool:
        return len(set(self.roles).intersection(set(roles))) > 0

    def is_expired(self) -> bool:
        return False if self.expiration_timestamp is None else self.expiration_timestamp <= datetime.utcnow().timestamp()

    def is_the_same_user(self, id):
        return self.id == id

    def is_admin(self):
        return "admin" in self.roles

    def set_preference(self, key: str, value: Any):
        self.preference[key] = value

    def delete_preference(self, key: str):
        if key in self.preference:
            del self.preference[key]

    def __str__(self):
        return f"User: {self.name}"

    def __repr__(self):
        return f"User: {self.name}"
