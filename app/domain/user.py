from typing import Optional, Any
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ..auth.user_db import token2user, UserDb

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    roles: Optional[list] = None
    disabled: bool

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.user_db = UserDb()
