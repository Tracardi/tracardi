from pydantic import BaseModel


class SignUpData(BaseModel):
    id: str = None
    username: str
    password: str
    type: str
    name: str
    url: str
    token: str = None
