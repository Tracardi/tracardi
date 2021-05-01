from datetime import datetime
from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends

from ..domain.time_range_query import TimeRangeQuery
from ..errors.errors import NullResponseError, convert_exception_to_json, RecordNotFound
from ..filters.datagrid import filter_event
from ..globals.authentication import get_current_user
from ..globals.context_server import context_server_via_uql
from ..globals.elastic_client import elastic_client
from ..storage.helpers import data_histogram, object_data

router = APIRouter(
    prefix="/event",
    dependencies=[Depends(get_current_user)]
)


@router.post("/chart/data")
async def event_data(query: TimeRangeQuery, elastic=Depends(elastic_client)):
    try:
        from_date_time, to_date_time = query.get_dates()  # type: datetime, datetime

        return object_data(
            elastic,
            'event',
            'timeStamp',
            from_date_time,
            to_date_time,
            query.offset,
            query.limit,
            time_zone=query.timeZone,
            query=query.query)

    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))


@router.post("/chart/histogram")
async def event_histogram(query: TimeRangeQuery, elastic=Depends(elastic_client)):
    try:

        from_date_time, to_date_time = query.get_dates()  # type: datetime, datetime

        return data_histogram(
            elastic,
            'event',
            'timeStamp',
            from_date_time,
            to_date_time,
            time_zone=query.timeZone,
            query=query.query)

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
                 "events": 0},
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


@router.get("/{id}")
async def event_get(id: str, uql=Depends(context_server_via_uql)):
    q = f"SELECT EVENT WHERE id=\"{id}\""

    try:
        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)

        if not result or 'list' not in result or not result['list']:
            raise RecordNotFound("Item not found")

        return result["list"][0]
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=convert_exception_to_json(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))


@router.post("/select")
async def event_select(request: Request, simplified: int = 1, limit: int = 20, uql=Depends(context_server_via_uql)):
    try:
        q = await request.body()
        q = q.decode('utf-8')
        if q:
            q = q.strip()
            q = f"SELECT EVENT WHERE {q} SORT BY timestamp DESC LIMIT {limit} "
        else:
            q = f"SELECT EVENT SORT BY timestamp DESC LIMIT {limit}"

        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)
        if simplified:
            return list(filter_event(result))
        else:
            return {
                'total': result['totalSize'],
                'data': result['list']
            }
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=convert_exception_to_json(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))
