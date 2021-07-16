from json import JSONDecodeError

from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/healthcheck")
async def track(r: Request):
    try:
        return await r.json()
    except JSONDecodeError as e:
        return await r.body()
