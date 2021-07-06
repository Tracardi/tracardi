import secrets
from elasticsearch import ElasticsearchException
from ..auth.user_db import token2user, UserDb
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

_singleton = None
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Authentication:

    def __init__(self):
        self.users_db = UserDb()
        self.token2user = token2user

    def authorize(self, username, password):  # username exists
        if not password:
            raise ValueError("Password empty")

        db_username_record = self.users_db.get_user(username)
        if not db_username_record:
            raise ValueError("Incorrect username or password")

        db_username = db_username_record['username']
        db_password = db_username_record['password']
        db_disabled = db_username_record["disabled"]

        if db_disabled:
            raise ValueError("This account was disabled")

        if db_username != username or db_password != password:
            raise ValueError("Incorrect username or password")

        return db_username_record

    @staticmethod
    def _generate_token():
        return secrets.token_hex(32)

    async def login(self, username, password):
        user_record = self.authorize(username, password)
        token = self._generate_token()
        # save token, match token with user in token2user
        await self.token2user.set(token, username)

        return {"access_token": token, "token_type": "bearer", "roles": user_record['roles']}

    async def logout(self, token):
        await self.token2user.delete(token)

    async def get_user_by_token(self, token):
        if await self.token2user.has(token):
            return await self.token2user.get(token)
        else:
            return None


def get_authentication():
    global _singleton

    def get_auth():
        return Authentication()

    if _singleton is None:
        _singleton = get_auth()

    return _singleton


async def get_current_user(token: str = Depends(oauth2_scheme)):

    try:
        auth = Authentication()
        user = await auth.get_user_by_token(token)
    except ElasticsearchException as e:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication exception",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
