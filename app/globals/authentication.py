import elasticsearch
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from ..auth.authentication import Authentication
from ..errors.errors import convert_exception_to_json

_singleton = None
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
        user = auth.get_user_by_token(token)
    except elasticsearch.exceptions.ElasticsearchException as e:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=convert_exception_to_json(e, "elasticsearch.exceptions.ElasticsearchException "),
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
