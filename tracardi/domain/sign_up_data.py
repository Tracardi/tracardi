from pydantic import BaseModel


class SignUpRecord(BaseModel):
    id: str = None
    host: str = None
    token: str = None


class SignUpData(BaseModel):
    id: str = None
    host: str
    username: str
    password: str
    type: str
    name: str
