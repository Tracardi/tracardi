from typing import List
from pydantic import BaseModel


class User(BaseModel):
    id: str
    username: str
    password: str
    full_name: str
    email: str
    roles: List[str]
    disabled: bool = False

