from typing import Optional

from tracardi.domain.entity import NullableEntity


class SignUpRecord(NullableEntity):
    token: Optional[str] = None


class SignUpData(NullableEntity):
    username: str
    password: str
    type: str
    name: str
