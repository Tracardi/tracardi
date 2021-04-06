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

    # async def factory(self, token: str = Depends(oauth2_scheme)):
    #     user = self._get_user_data_by_token(token)
    #     print(token)
    #     print(user)
    #     if not user or user.disabled:
    #         raise HTTPException(status_code=400, detail="Invalid user")
    #     return user
    #
    # def _get_user_data_by_token(self, token):
    #     if token in token2user:
    #         username = token2user[token]
    #         if username in self.user_db:
    #             return User(**self.user_db.get_user(username))
    #     return None
