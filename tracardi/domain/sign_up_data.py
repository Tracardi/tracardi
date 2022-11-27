from tracardi.domain.entity import NullableEntity


class SignUpRecord(NullableEntity):
    token: str = None


class SignUpData(NullableEntity):
    username: str
    password: str
    type: str
    name: str
