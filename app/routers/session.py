from datetime import datetime

from fastapi import APIRouter
from fastapi import HTTPException, Depends

from ..domain.time_range_query import TimeRangeQuery
from ..errors.errors import convert_exception_to_json
from ..globals.authentication import get_current_user
from ..globals.elastic_client import elastic_client
from ..storage.helpers import data_histogram, object_data

router = APIRouter(
    prefix="/session",
    # dependencies=[Depends(get_current_user)]
)


@router.post("/chart/data")
async def session_data(query: TimeRangeQuery, elastic=Depends(elastic_client)):
    try:
        from_date_time, to_date_time = query.get_dates()  # type: datetime, datetime
        return object_data(elastic, 'session', 'timeStamp',
                           from_date_time, to_date_time,
                           query.offset, query.limit,
                           query.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))


@router.post("/chart/histogram")
async def session_histogram(query: TimeRangeQuery, elastic=Depends(elastic_client)):
    try:
        from_date_time, to_date_time = query.get_dates()  # type: datetime, datetime
        return data_histogram(elastic, 'session', 'timeStamp',
                              from_date_time, to_date_time, query.query)
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
