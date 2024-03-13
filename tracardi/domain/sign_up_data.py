from tracardi.domain.entity import NullableEntity


class SignUpData(NullableEntity):
    username: str
    password: str
    type: str
    name: str
