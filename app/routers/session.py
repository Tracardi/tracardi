from datetime import datetime

from fastapi import APIRouter
from fastapi import HTTPException, Depends

from ..errors.errors import convert_exception_to_json
from ..globals.authentication import get_current_user
from ..globals.elastic_client import elastic_client
from ..storage.helpers import data_histogram, object_data

router = APIRouter(
    prefix="/session",
    dependencies=[Depends(get_current_user)]
)


@router.get("/chart/data")
async def session_data(min: datetime, max: datetime, offset: int = 0, limit: int = 20,
                     elastic=Depends(elastic_client), query: str = ""):
    try:
        return object_data(elastic, 'session', 'timeStamp', min, max, offset, limit, query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))


@router.get("/chart/histogram")
async def session_histogram(min: datetime, max: datetime, elastic=Depends(elastic_client), query: str = ""):
    try:
        return data_histogram(elastic, 'session', 'timeStamp', min, max, query)
    except Exception:
        return {
            "total": 0,
            "data": [
                {"time": 0,
                 "interval": 0,
                 "events": 0},
                {"time": 0,
                 "interval": 0,
                 "events": 0},
                {"time": 0,
                 "interval": 0,
                 "events": 0}
            ]
        }
