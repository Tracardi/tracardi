import json
from datetime import datetime
from time import sleep

from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends

from .. import config
from ..errors.errors import NullResponseError, convert_exception_to_json, RecordNotFound
from ..filters.datagrid import filter_event
from ..globals.authentication import get_current_user
from ..globals.context_server import context_server_via_uql
from ..globals.elastic_client import elastic_client
from ..storage.helpers import data_histogram, object_data
from ..storage.sql import to_sql

router = APIRouter(
    prefix="/event",
    # dependencies=[Depends(get_current_user)]
)


@router.get("/chart/data")
async def event_data(min: datetime, max: datetime, offset: int = 0, limit: int = 20,
                     elastic=Depends(elastic_client), query: str = ""):
    try:
        return object_data(elastic, 'event', 'timeStamp', min, max, offset, limit, query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))


@router.get("/chart/histogram")
async def event_histogram(min: datetime, max: datetime, elastic=Depends(elastic_client), query: str = ""):
    try:
        return data_histogram(elastic, 'event', 'timeStamp', min, max, query)
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
async def event_select(request: Request, uql=Depends(context_server_via_uql)):
    try:
        q = await request.body()
        q = q.decode('utf-8')
        if q:
            q = f"SELECT EVENT WHERE {q} SORT BY timeStamp DESC"
        else:
            q = "SELECT EVENT SORT BY timestamp DESC LIMIT 20"

        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)
        result = list(filter_event(result))
        return result
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=convert_exception_to_json(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))
