from datetime import datetime

from fastapi import APIRouter, Request
from fastapi import HTTPException, Depends
from ..errors.errors import NullResponseError, convert_exception_to_json
from ..filters.datagrid import filter_profile
from ..globals.authentication import get_current_user
from ..globals.context_server import context_server_via_uql
from ..globals.elastic_client import elastic_client
from ..storage.helpers import data_histogram, object_data

router = APIRouter(
    prefix="/profile",
    dependencies=[Depends(get_current_user)]
)


@router.get("/{id}")
async def profile_get(id: str, uql=Depends(context_server_via_uql)):
    q = f"SELECT PROFILE WHERE id=\"{id}\""

    try:
        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)
        return result["list"][0]
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select")
async def select_profiles(request: Request, uql=Depends(context_server_via_uql)):
    try:
        q = await request.body()
        q = q.decode('utf-8')
        if q:
            q = f"SELECT PROFILE WHERE {q} SORT BY systemProperties.lastUpdated DESC"
        else:
            q = "SELECT PROFILE SORT BY properties.lastVisit DESC"
        response_tuple = uql.select(q)
        result = uql.respond(response_tuple)
        result = list(filter_profile(result))
        return result
    except NullResponseError as e:
        raise HTTPException(status_code=e.response_status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chart/histogram")
async def profile_histogram(min: datetime, max: datetime, elastic=Depends(elastic_client), query: str = ""):
    try:
        return data_histogram(elastic, 'profile', 'properties.lastVisit', min, max, query)
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


@router.get("/chart/data")
async def profile_data(min: datetime, max: datetime, offset: int = 0, limit: int = 20,
                       elastic=Depends(elastic_client), query: str = ""):
    try:
        return object_data(elastic, 'profile', 'properties.lastVisit', min, max, offset, limit, query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=convert_exception_to_json(e))
